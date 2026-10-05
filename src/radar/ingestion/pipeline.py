"""Preparation, review and publication of documented quarterly financial facts."""
import calendar
import hashlib
import json
import re
import uuid
import threading
from functools import wraps
from datetime import date
from decimal import Decimal
from pathlib import Path

import duckdb
from radar import data
from radar.fx import brl_to_usd, mean_ptax_sales, balance_ptax_sale
from radar.ingestion.extract import extract, number
from radar.ingestion.sources import download, official, MAX_BYTES, fetch_ptax, fetch_yahoo, fetch_sec_companyfacts

FLOW = {'affiliates_net', 'jv_organic_contributions', 'nopat_disclosed', 'cfo', 'capex', 'dividends_paid', 'buybacks', 'ebit_adjusted', 'dda_adjusted', 'operating_tax', 'ebitda_reported'}
BALANCE = {'financial_debt_short', 'financial_debt_long', 'cash', 'cash_nonoperating',
           'equity_parent', 'equity_total', 'nci', 'leases', 'goodwill'}
CONCEPTS = {
    'affiliates_net': {'NET_EQUITY_ACCOUNTED_INCOME'},
    'jv_organic_contributions': {'ORGANIC_JV_CASH_CONTRIBUTIONS'},
    'nopat_disclosed': {'ADJUSTED_OPERATING_INCOME_AFTER_TAX'},
    'cfo': {'STATUTORY_CFO', 'CFO_EX_WORKING_CAPITAL', 'DACF'},
    'capex': {'ORGANIC_CASH_CAPEX', 'REPORTED_INVESTMENTS'},
    'dividends_paid': {'DIVIDENDS_PAID'}, 'buybacks': {'SETTLED_BUYBACKS'},
    'ebit_adjusted': {'ADJUSTED_EBIT'}, 'dda_adjusted': {'ADJUSTED_DDA'},
    'operating_tax': {'OPERATING_TAX'}, 'ebitda_reported': {'REPORTED_EBITDA'},
    'financial_debt_short': {'FINANCIAL_DEBT_SHORT'}, 'financial_debt_long': {'FINANCIAL_DEBT_LONG'},
    'cash': {'CASH_AND_EQUIVALENTS'}, 'cash_nonoperating': {'NONOPERATING_CASH'},
    'equity_parent': {'PARENT_EQUITY'}, 'equity_total': {'TOTAL_EQUITY_INCLUDING_NCI'},
    'nci': {'NCI'}, 'leases': {'LEASE_LIABILITIES'}, 'goodwill': {'GOODWILL'},
    'roce_reported': {'REPORTED_ROCE'},
}
NONCOMPARABLE = {'CFO_EX_WORKING_CAPITAL', 'DACF', 'REPORTED_INVESTMENTS'}
SCALE = {'units': Decimal('0.000001'), 'thousands': Decimal('0.001'), 'millions': Decimal(1), 'billions': Decimal(1000), 'percent': Decimal(1)}


_WRITE_LOCK=threading.RLock()

def serialized(function):
    @wraps(function)
    def call(*args,**kwargs):
        with _WRITE_LOCK:
            return function(*args,**kwargs)
    return call


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def period_dates(period):
    if not re.fullmatch(r'[12][0-9]{3}Q[1-4]', period):
        raise ValueError('Período exige AAAAQn.')
    year, quarter = int(period[:4]), int(period[-1])
    month = quarter * 3
    return date(year, month-2, 1), date(year, month, calendar.monthrange(year, month)[1])


def previous_period(period):
    period_dates(period)
    index = int(period[:4])*4+int(period[-1])-2
    return f'{index//4}Q{index%4+1}'


def connect():
    return duckdb.connect(str(data.ROOT/'database/radar.duckdb'))


@serialized
def initialize():
    data.initialize()
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS ingestion_batch(
            id VARCHAR PRIMARY KEY, fingerprint VARCHAR UNIQUE, company VARCHAR,
            mapping_version VARCHAR, rule_version VARCHAR, manifest VARCHAR, report VARCHAR,
            status VARCHAR, reviewer VARCHAR, review_note VARCHAR, created_at TIMESTAMP DEFAULT current_timestamp,
            reviewed_at TIMESTAMP, published_at TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS real_value(
            batch_id VARCHAR, company VARCHAR, period VARCHAR, field VARCHAR, value DECIMAL(28,10),
            comparable BOOLEAN, reason VARCHAR, metadata VARCHAR,
            published_at TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY(batch_id,period,field))''')
        db.execute('''CREATE TABLE IF NOT EXISTS api_snapshot(
            hash VARCHAR, provider VARCHAR, scope VARCHAR, payload VARCHAR,
            created_at TIMESTAMP DEFAULT current_timestamp, PRIMARY KEY(hash,provider,scope))''')


@serialized
def save_snapshot(result):
    initialize()
    with connect() as db:
        db.execute('INSERT INTO api_snapshot(hash,provider,scope,payload) VALUES (?,?,?,?) ON CONFLICT DO NOTHING',
                   [result['hash'], result['provider'], result['scope'], dumps(result)])
    return result


def snapshots():
    initialize()
    with connect() as db:
        return [json.loads(row[0]) for row in db.execute('SELECT payload FROM api_snapshot ORDER BY created_at').fetchall()]


def get_batch(batch_id):
    initialize()
    with connect() as db:
        row = db.execute('SELECT id,company,status,reviewer,review_note,report FROM ingestion_batch WHERE id=?', [batch_id]).fetchone()
    if not row:
        raise ValueError('Lote não encontrado.')
    return dict(zip(('id','company','status','reviewer','review_note','report'), row[:-1]+(json.loads(row[-1]),)))


def batches():
    initialize()
    with connect() as db:
        return db.execute('SELECT id,company,mapping_version,rule_version,status,reviewer,created_at,published_at FROM ingestion_batch ORDER BY created_at DESC').df()


def _validate_manifest(manifest):
    company = manifest.get('company')
    if company not in data.COMPANIES:
        raise ValueError('Empresa não pertence ao conjunto ativo.')
    if manifest.get('schema_version') != 1 or not manifest.get('mapping_version'):
        raise ValueError('schema_version=1 e mapping_version obrigatórios.')
    if manifest.get('accounting_standard') != data.COMPANIES[company][1]:
        raise ValueError('Padrão contábil diverge do cadastro IFRS/US GAAP.')
    if not manifest.get('mapping_note') or not manifest.get('observations'):
        raise ValueError('Mapeamento exige justificativa e observações.')
    docs = manifest.get('documents', [])
    ids = [doc['id'] for doc in docs]
    if len(set(ids)) != len(ids):
        raise ValueError('IDs de documentos duplicados.')
    ids = [o['id'] for o in manifest['observations']]
    if len(ids) != len(set(ids)):
        raise ValueError('IDs de observações duplicados.')
    if len(docs)==0:
        raise ValueError('Documentos de origem obrigatórios.')
    keys = set()
    for o in manifest['observations']:
        document=next((d for d in docs if d['id']==o['document']),None)
        if document is None or document.get('format') not in ('pdf','xlsx','csv','json','html'):
            raise ValueError('Documento/formato inválido no mapeamento.')
        if document['format'] in ('pdf','xlsx') and not o.get('selector',{}).get('guards'):
            raise ValueError('PDF/XLSX exige guards para verificar cabeçalhos/rótulos.')
        start,end=period_dates(o['period'])
        if o.get('selector',{}).get('taxonomy'):
            sel=o['selector'];where=sel.get('where',{})
            if not sel.get('guards') or where.get('end')!=str(end) or sel.get('unit')!=o['currency'] or o['scale']!='units':
                raise ValueError('XBRL exige identificação do emissor, data final, unidade original e escala units.')
            if o['period_type']!='BALANCE':
                expected_start=str(date(end.year,1,1)) if o['period_type']=='YTD' else str(start)
                if where.get('start')!=expected_start:
                    raise ValueError('Duração XBRL diverge do trimestre/acumulado declarado.')
        field = o.get('field')
        if field and (field not in CONCEPTS or o.get('concept') not in CONCEPTS[field]):
            raise ValueError(f'Conceito inválido para {field}.')
        if o.get('currency') not in ('BRL','USD') or o.get('scale') not in SCALE:
            raise ValueError('Moeda/escala não aprovada. Suporte: BRL/USD e escala explícita.')
        if field == 'roce_reported' and (o['scale'] != 'percent' or o['basis'] != 'REPORTED'):
            raise ValueError('ROCE reportado exige escala percent e basis REPORTED.')
        if field and field != 'roce_reported' and o['scale'] == 'percent':
            raise ValueError('Componente monetário não pode usar escala percent.')
        if o.get('basis') not in ('REPORTED','RECONSTRUCTED') or not o.get('scope'):
            raise ValueError('basis e perímetro/scope obrigatórios.')
        expected = 'BALANCE' if field in BALANCE else None
        if o.get('period_type') not in ('QUARTER','YTD','BALANCE') or (expected and o['period_type'] != expected):
            raise ValueError('Tipo de período inválido para o campo.')
        if field in FLOW and o['period_type'] == 'BALANCE':
            raise ValueError('Fluxo não pode ser tratado como saldo.')
        if field == 'roce_reported' and o['period_type'] != 'QUARTER':
            raise ValueError('ROCE reportado deve ser identificado no trimestre da divulgação.')
        if not o.get('comparable', True) and not o.get('comparability_reason'):
            raise ValueError('Não comparabilidade exige motivo.')
        if field:
            key = (o['period'], field)
            if key in keys:
                raise ValueError('Campo/período duplicado; concilie fontes antes da carga.')
            keys.add(key)
        if field in ('financial_debt_short', 'financial_debt_long') and not isinstance(o.get('includes_leases'), bool):
            raise ValueError('Dívida exige includes_leases explícito.')
        if field == 'jv_organic_contributions' and (o['basis'] != 'RECONSTRUCTED' or not o.get('policy_note')):
            raise ValueError('Aportes orgânicos em JV exigem reconstrução e classificação documentada, excluindo M&A e empréstimos financeiros.')
        if field in ('ebit_adjusted', 'dda_adjusted') and not o.get('adjustment_set'):
            raise ValueError('EBIT/DD&A exigem identificação dos mesmos ajustes.')
        if field == 'operating_tax' and not o.get('adjustment_set'):
            raise ValueError('Imposto exige identificação dos ajustes do EBIT.')
        if field == 'operating_tax' and o.get('tax_method') not in ('DISCLOSED','RECONSTRUCTED'):
            raise ValueError('Imposto real exige divulgação/reconstrução operacional. Alíquota sintética proibida.')


@serialized
def stage(manifest, *, base_dir=None, allow_download=False, client=None):
    """Prepare an immutable batch; no financial data becomes visible on this call."""
    initialize()
    _validate_manifest(manifest)
    company = manifest['company']
    base_dir = Path(base_dir or '.')
    docs, errors = {}, []
    for doc in manifest['documents']:
        try:
            if doc.get('hash'):
                if not re.fullmatch(r'[a-f0-9]{64}',doc['hash']):
                    raise ValueError('Hash SHA-256 inválido.')
                content = (data.ROOT/'data/original'/doc['hash']).read_bytes()
                if hashlib.sha256(content).hexdigest() != doc['hash']:
                    raise ValueError('Hash do documento não confere.')
            elif doc.get('path'):
                content = (base_dir/doc['path']).read_bytes()
            elif allow_download:
                content, resolved = download(doc['url'], company, client=client)
                doc={**doc,'resolved_url':resolved}
            else:
                raise ValueError('Documento ausente. Use hash/path ou habilite download.')
            if doc['url'].startswith('https://data.sec.gov/'):
                payload=json.loads(content)
                if not doc.get('issuer_cik') or int(payload['cik'])!=int(doc['issuer_cik']):
                    raise ValueError('Documento SEC exige CIK do emissor e identidade coincidente.')
            if len(content) > MAX_BYTES:
                raise ValueError('Documento excede 20 MB.')
            digest = hashlib.sha256(content).hexdigest()
            if doc.get('expected_hash') and doc['expected_hash'] != digest:
                raise ValueError('Documento mudou; hash diverge do mapeamento aprovado.')
            digest, _ = data.preserve(content, doc.get('filename', doc['id']+'.'+doc['format']),
                                      company, doc.get('period', manifest['observations'][0]['period']), doc['url'], 'Mapeamento '+manifest['mapping_version'])
            docs[doc['id']] = {**doc, 'hash': digest, 'official': official(doc['url'], company)}
        except Exception as exc:
            # A failed acquisition is recorded, never converted into a zero.
            errors.append({'document': doc['id'], 'error': str(exc)})
    raw = {}
    for observation in manifest['observations']:
        try:
            doc = docs[observation['document']]
            value, locator = extract(data.ROOT/'data/original'/doc['hash'], doc['format'], observation['selector'])
            parsed = number(value, observation.get('locale','en'), dash_zero=observation.get('dash_zero',False))
            sign = number(observation.get('sign',1))
            if sign not in (Decimal(1), Decimal(-1)):
                raise ValueError('Sinal deve ser +1 ou -1, explicitamente.')
            raw[observation['id']] = {**observation, 'raw_value': str(value), 'value': str(parsed*SCALE[observation['scale']]*sign),
                                      'hash': doc['hash'], 'url': doc['url'], 'locator': locator, 'official': doc['official']}
        except Exception as exc:
            errors.append({'observation': observation['id'], 'field': observation.get('field'), 'period': observation['period'], 'error': str(exc)})
    fx = manifest.get('fx')
    rates={};fx_snapshots=[]
    if fx is not None:
        hashes=fx if isinstance(fx,list) else [fx]
        saved=snapshots()
        for digest in hashes:
            snapshot=next((s for s in saved if s['provider']=='Bacen' and s['hash']==digest),None)
            if not snapshot:
                raise ValueError('Snapshot PTAX Bacen não encontrado.')
            payload=(data.ROOT/'data/original'/digest).read_bytes()
            if hashlib.sha256(payload).hexdigest()!=digest:
                raise ValueError('Hash PTAX inválido.')
            for day,rate in snapshot['rates'].items():
                if day in rates and rates[day]!=rate:
                    raise ValueError('Snapshots PTAX conflitantes para o mesmo dia.')
                rates[day]=rate
            fx_snapshots.append(snapshot)
    def covered(start,end):
        intervals=sorted((date.fromisoformat(s['start']),date.fromisoformat(s['end'])) for s in fx_snapshots)
        from datetime import timedelta
        cursor=start
        for a,b in intervals:
            if a>cursor:break
            if b>=cursor:cursor=b+timedelta(days=1)
        return cursor>end
    points = []
    by_key = {(o['period'],o.get('field')):o for o in raw.values() if o.get('field')}
    for item in raw.values():
        if not item.get('field'):
            continue
        point = {k:item.get(k) for k in ('id','period','field','concept','basis','scope','hash','url','locator','currency','scale','period_type','raw_value','adjustment_set','tax_method','includes_leases')}
        point.update({'value': None, 'comparable': item.get('comparable',True), 'reasons': [], 'flags': [], 'lineage': [item['id']], 'checks': {}})
        if item.get('policy_note'):
            point['policy_note'] = item['policy_note']
            point['flags'].append('DOCUMENTED_APPROXIMATION')
        try:
            value = Decimal(item['value'])
            for adjustment in item.get('adjustments', []):
                other = raw[adjustment['observation']]
                if not adjustment.get('reason') or any(other[k] != item[k] for k in ('currency','period','period_type','scope')):
                    raise ValueError('Ajuste exige razão e mesma moeda/período/perímetro.')
                value += Decimal(other['value'])*number(adjustment['coefficient'])
                point['lineage'].append(other['id'])
                point['flags'].append('DOCUMENTED_ADJUSTMENT')
            if item['period_type'] == 'YTD' and item['period'][-1] != '1':
                previous = by_key.get((previous_period(item['period']), item['field']))
                if not previous or any(previous[k] != item[k] for k in ('currency','period_type','scope','basis','concept')) or previous.get('adjustment_set') != item.get('adjustment_set'):
                    raise ValueError('Acumulado anterior compatível ausente; não converter para trimestre.')
                # Adjust both cumulative values before subtraction.
                previous_value = Decimal(previous['value'])
                for adj in previous.get('adjustments', []):
                    prev_adj = raw[adj['observation']]
                    if not adj.get('reason') or any(prev_adj[k] != previous[k] for k in ('currency','period','period_type','scope')):
                        raise ValueError('Ajuste do acumulado anterior inválido.')
                    previous_value += Decimal(prev_adj['value'])*number(adj['coefficient'])
                    point['lineage'].append(prev_adj['id'])
                value -= previous_value
                if not previous.get('comparable',True) or previous['concept'] in NONCOMPARABLE:
                    point['comparable']=False
                    point['reasons'].append('Acumulado anterior não comparável.')
                point['lineage'].append(previous['id'])
                point['flags'].append('DERIVED_QUARTER')
            start, end = period_dates(item['period'])
            if item['currency'] == 'BRL' and item['field'] != 'roce_reported':
                if item['period_type'] == 'BALANCE':
                    selected = balance_ptax_sale(str(end), rates)
                    if selected is None:
                        raise ValueError('PTAX de fechamento anterior/igual ausente.')
                    day, rate = selected
                    point['fx_date'] = day
                    point['fx_fallback'] = day != str(end)
                else:
                    if not covered(start,end):
                        raise ValueError('Snapshot PTAX não cobre todo o trimestre.')
                    rate = mean_ptax_sales([v for k,v in rates.items() if str(start)<=k<=str(end)])
                    if rate is None:
                        raise ValueError('PTAX média trimestral ausente.')
                value = brl_to_usd(value, rate)
                point['fx_rate'] = str(rate)
                point['fx_hash'] = [s['hash'] for s in fx_snapshots]
            if item['field'] in ('jv_organic_contributions','capex','dividends_paid','buybacks','financial_debt_short','financial_debt_long','cash','cash_nonoperating','leases','goodwill') and value<0:
                raise ValueError('Componente exige valor positivo/zero na base comum; confira sinal e conceito.')
            if item['concept'] in NONCOMPARABLE:
                point['comparable'] = False
                point['reasons'].append('Conceito divulgado não atende à base padronizada: '+item['concept'])
            if not item.get('comparable',True):
                point['reasons'].append(item['comparability_reason'])
            point['value'] = str(value)
            ancestors = [raw[key] for key in point['lineage']]
            point['checks'] = {'source_official': all(a['official'] for a in ancestors), 'document_hash': all(a['hash'] for a in ancestors),
                               'locator': all(a['locator'] for a in ancestors), 'company': True, 'period': True,
                               'currency': True, 'scale': True, 'unique': True, 'valid_calculation': value.is_finite()}
            for check, passed in point['checks'].items():
                if not passed:
                    point['reasons'].append('Controle essencial reprovado: '+check)
        except (ValueError, KeyError, ArithmeticError) as exc:
            point['reasons'].append(str(exc))
        point['state'] = 'REVISAO' if point['value'] is not None and all(point['checks'].values()) and point['checks'] else 'BLOQUEADO'
        points.append(point)
    # Reconciliation expressed as an explicit signed bridge, with independent
    # source observations. It is evaluated in original units before conversion.
    bridges = []
    for bridge in manifest.get('reconciliations', []):
        result = {**bridge, 'passed': False}
        try:
            reference_terms = bridge.get('reference_terms')
            if reference_terms:
                if bridge.get('reference') or not reference_terms:
                    raise ValueError('Escolha referência única ou ponte de referência.')
                reference_sources = [raw[t['observation']] for t in reference_terms]
                reference = dict(reference_sources[0])
                if not all(all(s[k] == reference[k] for k in ('currency','scope','period','period_type')) for s in reference_sources):
                    raise ValueError('Componentes da referência usam bases incompatíveis.')
                reference['value'] = str(sum(Decimal(s['value'])*number(t['coefficient']) for s,t in zip(reference_sources,reference_terms)))
            else:
                reference_sources = [raw[bridge['reference']]]
                reference = reference_sources[0]
            terms = [raw[t['observation']] for t in bridge['terms']]
            sum_quarters=bridge.get('aggregation')=='SUM_QUARTERS'
            compatible=all(all(t[k]==reference[k] for k in ('currency','scope')) for t in terms)
            if sum_quarters:
                year=reference['period'][:4]
                compatible=compatible and reference['period_type']=='YTD' and reference['period'].endswith('Q4') and len(terms)==4 and {t['period'] for t in terms}=={year+'Q'+str(q) for q in range(1,5)} and all(t['period_type']=='QUARTER' for t in terms)
            else:
                compatible=compatible and all(all(t[k]==reference[k] for k in ('period','period_type')) for t in terms)
            if not bridge.get('reason') or not terms or not compatible:
                raise ValueError('Ponte exige motivo e bases compatíveis.')
            if {s['id'] for s in reference_sources} & {t['observation'] for t in bridge['terms']}:
                raise ValueError('Referência de conciliação deve ser independente dos termos.')
            if not all(t['official'] for t in terms+reference_sources):
                raise ValueError('Ponte exige fontes oficiais.')
            calculated = sum(Decimal(t['value'])*number(term['coefficient']) for t,term in zip(terms,bridge['terms']))
            ref = Decimal(reference['value'])
            rate = Decimal(1)
            if reference['currency']=='BRL':
                start,end = period_dates(reference['period'])
                if reference['period_type']=='YTD':
                    start = date(end.year,1,1)
                if reference['period_type']=='BALANCE':
                    selected=balance_ptax_sale(str(end),rates)
                    if selected is None:raise ValueError('Conciliação sem PTAX de fechamento.')
                    rate=selected[1]
                else:
                    if not covered(start,end):
                        raise ValueError('Conciliação sem cobertura PTAX.')
                    rate=mean_ptax_sales([v for k,v in rates.items() if str(start)<=k<=str(end)])
            policy=data.RULES['quality_policy']
            tolerance=max(Decimal(str(policy['reconciliation_absolute_usd_million'])), abs(ref/rate)*Decimal(str(policy['reconciliation_relative'])), number(bridge.get('rounding_usd_million',0)))
            difference=(calculated-ref)/rate
            result.update({'calculated_original_million':str(calculated),'reference_original_million':str(ref),
                           'difference_usd_million':str(difference),'tolerance_usd_million':str(tolerance),
                           'passed':abs(difference)<=tolerance})
        except (KeyError,ValueError,ArithmeticError) as exc:
            result['error']=str(exc)
        bridges.append(result)
        for point in points:
            if point['id'] in bridge.get('applies_to', []):
                if bridge.get('aggregation')=='SUM_QUARTERS':
                    expected={p['id']:Decimal(1) for p in points if p['id'] in bridge.get('applies_to',[]) and p['field']==point['field']}
                else:
                    expected={point['id']: Decimal(1)}
                for adj in raw[point['id']].get('adjustments',[]):
                    expected[adj['observation']]=expected.get(adj['observation'],Decimal(0))+number(adj['coefficient'])
                actual={}
                for term in bridge['terms']:
                    actual[term['observation']]=actual.get(term['observation'],Decimal(0))+number(term['coefficient'])
                if actual != expected:
                    result['passed']=False
                    result['error']='Ponte não corresponde ao valor/ajustes do componente.' 
                point['reconciliations'] = point.get('reconciliations', [])+[bridge['id']]
                if not result['passed']:
                    point['state']='BLOQUEADO' if result.get('error') else 'REVISAO'
                    point['reasons'].append('Conciliação pendente/fora da tolerância: '+bridge['id'])
    for point in points:
        item=raw[point['id']]
        if (item.get('adjustments') or item['basis']=='RECONSTRUCTED' or item.get('field') in ('ebit_adjusted','dda_adjusted','operating_tax','ebitda_reported','nopat_disclosed','jv_organic_contributions')) and not point.get('reconciliations'):
            point['reasons'].append('Reconciliação documentada obrigatória para reconstrução/ajustes.')
        # Alert on current vs previous normalized quarter, with no demo fallback.
        previous=next((p for p in points if p['period']==previous_period(point['period']) and p['field']==point['field'] and p['value'] is not None),None)
        if previous and point['value'] is not None:
            old,new=Decimal(previous['value']),Decimal(point['value'])
            if (old==0 and new!=0) or (old!=0 and abs(new-old)/abs(old)>Decimal(str(data.RULES['quality_policy']['variation_alert_relative']))):
                point['flags'].append('VARIATION_ALERT')
    fingerprint=hashlib.sha256(dumps({'manifest':manifest,'raw':raw,'fx_hash':fx,'rule_version':data.RULES['version']}).encode()).hexdigest()
    report={'company':company,'mapping_version':manifest['mapping_version'],'rule_version':data.RULES['version'],
            'raw':list(raw.values()),'documents':list(docs.values()),'points':points,'reconciliations':bridges,'errors':errors,
            'pending_components':manifest.get('pending_components',[]),
            'note':'Preparação não publica. Ausências não usam dados sintéticos; LTM exige quatro trimestres.'}
    with connect() as db:
        existing=db.execute('SELECT id FROM ingestion_batch WHERE fingerprint=?',[fingerprint]).fetchone()
        if existing:
            return get_batch(existing[0])
        batch_id=uuid.uuid4().hex
        db.execute('INSERT INTO ingestion_batch(id,fingerprint,company,mapping_version,rule_version,manifest,report,status) VALUES (?,?,?,?,?,?,?,?)',
                   [batch_id,fingerprint,company,manifest['mapping_version'],data.RULES['version'],dumps(manifest),dumps(report),'REVISAO'])
    return get_batch(batch_id)


@serialized
def approve(batch_id, reviewer, note, *, accept_alerts=False, fields=None):
    """One reviewer approves selected valid points; unresolved checks cannot pass."""
    if not reviewer.strip() or not note.strip():
        raise ValueError('Informe responsável e justificativa da revisão.')
    batch=get_batch(batch_id)
    if batch['status']=='PUBLICADO':
        raise ValueError('Lote publicado é imutável; crie outra versão.')
    report=batch['report']
    selected=[]
    for point in report['points']:
        if fields is not None and point['field'] not in fields:
            continue
        failed_bridges=[b for b in report['reconciliations'] if point['id'] in b.get('applies_to',[]) and not b['passed']]
        unresolved=any('Reconciliação documentada obrigatória' in r for r in point['reasons'])
        if point['state']=='BLOQUEADO' or point['value'] is None or failed_bridges or unresolved:
            continue
        if 'VARIATION_ALERT' in point['flags'] and not accept_alerts:
            continue
        point['state']='ALERTA_ACEITO' if 'VARIATION_ALERT' in point['flags'] else 'APROVADO'
        selected.append(point)
    if not selected:
        raise ValueError('Nenhum campo elegível. Resolva controles/conciliações ou aceite os alertas documentados.')
    with connect() as db:
        db.execute("UPDATE ingestion_batch SET report=?,status='APROVADO',reviewer=?,review_note=?,reviewed_at=current_timestamp WHERE id=? AND status<>'PUBLICADO'",
                   [dumps(report),reviewer,note,batch_id])
    return get_batch(batch_id)


@serialized
def publish(batch_id):
    batch=get_batch(batch_id)
    if batch['status']=='PUBLICADO':
        return batch
    if batch['status']!='APROVADO':
        raise ValueError('Publicação exige revisão e aprovação explícita.')
    points=[p for p in batch['report']['points'] if p['state'] in ('APROVADO','ALERTA_ACEITO')]
    with connect() as db:
        db.execute('BEGIN TRANSACTION')
        for point in points:
            db.execute('INSERT INTO real_value(batch_id,company,period,field,value,comparable,reason,metadata) VALUES (?,?,?,?,?,?,?,?)',
                       [batch_id,batch['company'],point['period'],point['field'],point['value'],point['comparable'],'; '.join(point['reasons']),dumps(point)])
            db.execute('INSERT INTO reporting_period(period) VALUES (?) ON CONFLICT DO NOTHING',[point['period']])
        db.execute("UPDATE ingestion_batch SET status='PUBLICADO',published_at=current_timestamp WHERE id=?",[batch_id])
        db.execute('COMMIT')
    return get_batch(batch_id)
