"""Approved real observations reconstructed into the benchmark's common basis."""
import json
from decimal import Decimal
import duckdb
import pandas as pd
from radar import data
from radar.ingestion.pipeline import period_dates, previous_period


FIELDS = ['jv_organic_contributions','nopat_disclosed','cfo','capex','distribution','debt','ebitda','leases','roce'] + data.ROCE_FIELDS


def published_points():
    with duckdb.connect(str(data.ROOT/'database/radar.duckdb'),read_only=True) as db:
        if not db.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='real_value'").fetchone()[0]:
            return []
        rows = db.execute('''SELECT company,period,field,value,comparable,reason,metadata,batch_id
            FROM real_value QUALIFY row_number() OVER(PARTITION BY company,period,field ORDER BY published_at DESC,batch_id DESC)=1
            ORDER BY company,period,field''').fetchall()
    return [dict(zip(('company','period','field','value','comparable','reason','metadata','batch_id'),row),
                 details=json.loads(row[6])) for row in rows]


def rows():
    points=published_points()
    grouped={}
    for point in points:
        grouped.setdefault((point['company'],point['period']),{})[point['field']]=point
    result=[]
    for (company,period),fields in sorted(grouped.items()):
        row={'company':company,'period':period,'version':1,'mode':'REAL', **{k:None for k in FIELDS}}
        quality={}
        def compose(target, terms):
            required=[fields.get(field) for field,_ in terms]
            if any(p is None for p in required):
                quality[target]={'status':'INDISPONIVEL','reason':'Componentes ausentes: '+', '.join(f for f,_ in terms if f not in fields)}
                return None
            scopes={p['details']['scope'] for p in required}
            if len(scopes)!=1:
                quality[target]={'status':'NAO_COMPARAVEL','reason':'Perímetros incompatíveis entre componentes.'}
                return None
            noncomparable=[p for p in required if not p['comparable']]
            if noncomparable:
                quality[target]={'status':'NAO_COMPARAVEL','reason':'; '.join(p['reason'] for p in noncomparable)}
            return sum(p['value']*Decimal(coefficient) for p,(_,coefficient) in zip(required,terms))
        for field in ('jv_organic_contributions','nopat_disclosed','cfo','capex','leases','ebit_adjusted','operating_tax','goodwill_close'):
            source='goodwill' if field=='goodwill_close' else field
            row[field]=compose(field,[(source,1)])
        row['roce']=compose('reported_roce',[('roce_reported',1)])
        row['distribution']=compose('distribution',[('dividends_paid',1),('buybacks',1)])
        row['ebitda']=compose('ebitda',[('ebit_adjusted',1),('dda_adjusted',1)])
        alternative=data.RULES.get('ebitda_policy',{}).get('disclosed_alternative',{})
        if row['ebitda'] is None and company in alternative.get('companies',[]) and alternative.get('status')=='APROVADO' and 'ebitda_reported' in fields:
            row['ebitda']=compose('ebitda',[('ebitda_reported',1)])
            row['_ebitda_method']='DISCLOSED_ALTERNATIVE'
        if row['ebitda'] is not None and row.get('_ebitda_method')!='DISCLOSED_ALTERNATIVE' and fields['ebit_adjusted']['details']['adjustment_set']!=fields['dda_adjusted']['details']['adjustment_set']:
            row['ebitda']=None
            quality['ebitda']={'status':'NAO_COMPARAVEL','reason':'EBIT e DD&A usam conjuntos de ajustes distintos.'}
        debt_terms=[('financial_debt_short',1),('financial_debt_long',1)]
        debt=compose('financial_debt',debt_terms)
        if debt is not None:
            short=fields['financial_debt_short']['details']['includes_leases']
            long=fields['financial_debt_long']['details']['includes_leases']
            if short != long:
                # Separate short/long lease split is required for mixed definitions.
                debt=None
                quality['financial_debt']={'status':'NAO_COMPARAVEL','reason':'Dívida CP/LP diverge quanto a leases; requer abertura por prazo.'}
            elif short:
                leases=compose('financial_debt',[('leases',1)])
                debt=debt-leases if leases is not None else None
        cash=compose('debt',[('cash',1)])
        row['debt']=debt-cash if debt is not None and cash is not None else None
        if row['debt'] is not None and len({fields[k]['details']['scope'] for k in ('financial_debt_short','financial_debt_long','cash')})!=1:
            row['debt']=None
            quality['debt']={'status':'NAO_COMPARAVEL','reason':'Perímetros de dívida e caixa incompatíveis.'}
        if quality.get('financial_debt',{}).get('status')=='NAO_COMPARAVEL':
            quality['debt']=quality['financial_debt']
        equity_terms=[('equity_parent',1),('nci',1)] if 'equity_parent' in fields else [('equity_total',1)]
        equity=compose('capital_employed_close',equity_terms)
        nonoperating=compose('capital_employed_close',[('cash_nonoperating',1)])
        ce_fields=[f for f,_ in equity_terms]+['financial_debt_short','financial_debt_long','cash_nonoperating']
        if debt is not None and fields['financial_debt_short']['details']['includes_leases']:
            ce_fields.append('leases')
        if debt is not None and equity is not None and nonoperating is not None:
            if len({fields[f]['details']['scope'] for f in ce_fields})==1:
                row['capital_employed_close']=equity+debt-nonoperating
            else:
                quality['capital_employed_close']={'status':'NAO_COMPARAVEL','reason':'Perímetros incompatíveis na composição do capital.'}
        for target, dependencies in [('debt',['financial_debt_short','financial_debt_long','cash','leases'] if fields.get('financial_debt_short',{}).get('details',{}).get('includes_leases') else ['financial_debt_short','financial_debt_long','cash']),('capital_employed_close',ce_fields)]:
            bad=[fields[f] for f in dependencies if f in fields and not fields[f]['comparable']]
            if bad:quality[target]={'status':'NAO_COMPARAVEL','reason':'; '.join(p['reason'] for p in bad)}
        # Operating tax must match the EBIT adjustment perimeter, never synthetic rates.
        if row['operating_tax'] is not None:
            ebit=fields.get('ebit_adjusted')
            tax=fields['operating_tax']
            if not ebit or tax['details'].get('adjustment_set')!=ebit['details']['adjustment_set'] or tax['details']['scope']!=ebit['details']['scope']:
                row['operating_tax']=None
                quality['operating_tax']={'status':'NAO_COMPARAVEL','reason':'Imposto operacional incompatível com o EBIT ajustado.'}
        alternative=data.RULES.get('operating_tax',{}).get('normalized_alternative',{})
        if row['operating_tax'] is None and row['nopat_disclosed'] is None and company in alternative.get('companies',[]) and alternative.get('status')=='APROVADO' and row['ebit_adjusted'] is not None:
            affiliates=compose('operating_tax',[('affiliates_net',1)])
            if affiliates is not None and fields['affiliates_net']['details']['scope']==fields['ebit_adjusted']['details']['scope']:
                row['operating_tax']=(row['ebit_adjusted']-affiliates)*Decimal(alternative['rate'])
                row['_tax_method']='NORMALIZED_RATE'
                quality['operating_tax']={'status':'NAO_COMPARAVEL','reason':'Alternativa Petrobras aprovada: imposto estimado normalizado de 34% sobre EBIT ajustado sem investidas; investidas mantidas já líquidas. Capital reconstruído RADAR; não reproduz ROCE divulgado nem imposto incorrido.'}
        row['_quality']=quality
        row['_scope']={k:p['details']['scope'] for k,p in fields.items()}
        result.append(row)
    indexed={(r['company'],r['period']):r for r in result}
    for row in result:
        previous=indexed.get((row['company'],previous_period(row['period'])))
        for opening,closing in [('capital_employed_open','capital_employed_close'),('leases_open','leases'),('goodwill_open','goodwill_close')]:
            row[opening]=previous[closing] if previous else None
            if previous and closing in previous['_quality']:
                row['_quality'][opening]=previous['_quality'][closing]
    return result


def facts():
    return pd.DataFrame(rows(),columns=['company','period',*FIELDS,'version','mode','_quality','_scope','_ebitda_method'])


def quality(window, metric, leases=False, exclude_goodwill=False, include_jv=False):
    dependencies={'cfo':['cfo'],'capex':['capex','cfo'],'distribution':['distribution','cfo'],
                  'leverage':['debt','ebitda'],'roce':['ebit_adjusted','operating_tax','capital_employed_open','capital_employed_close'],
                  'fcf':['cfo','capex'],'residual':['cfo','capex','distribution']}
    keys=dependencies[metric][:]
    if metric=='roce' and all(r.get('nopat_disclosed') is not None for r in window):
        keys=['nopat_disclosed','capital_employed_open','capital_employed_close']
    if include_jv and metric in ('capex','fcf','residual'):
        keys+=['jv_organic_contributions']
    if leases and metric in ('leverage','roce'):
        keys+=['leases'] if metric=='leverage' else ['leases_open','leases']
    if exclude_goodwill and metric=='roce':keys+=['goodwill_open','goodwill_close']
    if len(window)!=4:
        return {'status':'INDISPONIVEL','reason':'LTM exige quatro trimestres reais consecutivos aprovados.'}
    relevant=[]
    if include_jv and metric in ('capex','fcf','residual'):
        for row in window:
            scopes=row.get('_scope',{})
            if scopes.get('jv_organic_contributions') and scopes.get('capex') != scopes.get('jv_organic_contributions'):
                relevant.append({'status':'NAO_COMPARAVEL','reason':'Perímetros incompatíveis entre CAPEX e aportes orgânicos em JVs.'})
    for index,row in enumerate(window):
        use=keys
        if metric=='leverage' and index!=3:use=[k for k in keys if k not in ('debt','leases')]
        if metric=='roce':
            use=[k for k in keys if (not k.endswith('_open') or index==0) and (k not in ('capital_employed_close','goodwill_close','leases') or index==3)]
        for k in use:
            if row.get(k) is None:
                reason=row.get('_quality',{}).get(k,{}).get('reason', 'Componente ausente: '+k)
                relevant.append({'status':'NAO_COMPARAVEL' if metric=='roce' and k=='operating_tax' else 'INDISPONIVEL','reason':reason})
            elif row.get('_quality',{}).get(k,{}).get('status')=='NAO_COMPARAVEL':
                relevant.append(row['_quality'][k])
    for field in ('ebitda_reported','jv_organic_contributions','nopat_disclosed','cfo','capex','dividends_paid','buybacks','ebit_adjusted','dda_adjusted','operating_tax'):
        dependent={'ebitda_reported':['leverage'],'jv_organic_contributions':['capex','fcf','residual'] if include_jv else [],'nopat_disclosed':['roce'],'cfo':['cfo'],'capex':['capex','cfo','fcf','residual'],'dividends_paid':['distribution','residual'],
                   'buybacks':['distribution','residual'],'ebit_adjusted':['roce','leverage'],'dda_adjusted':['leverage'],'operating_tax':['roce']}
        if metric in dependent[field]:
            scopes={r.get('_scope',{}).get(field) for r in window if r.get('_scope',{}).get(field)}
            if len(scopes)>1:
                relevant.append({'status':'NAO_COMPARAVEL','reason':'Mudança de perímetro sem conciliação: '+field})
    if metric=='leverage' and any(r.get('_ebitda_method')=='DISCLOSED_ALTERNATIVE' for r in window):
        relevant.append({'status':'NAO_COMPARAVEL','reason':'Alternativa aprovada: dívida líquida reconstruída / EBITDA ajustado divulgado. Equivalência à regra comum não comprovada; comparabilidade entre peers pendente.'})
    if relevant:
        return {'status':'NAO_COMPARAVEL' if any(p['status']=='NAO_COMPARAVEL' for p in relevant) else 'INDISPONIVEL',
                'reason':'; '.join(dict.fromkeys(p['reason'] for p in relevant))}
    return {'status':'COMPARAVEL','reason':('Método alternativo aprovado: numerador ajustado divulgado + capital empregado reconstruído; caixa integral como aproximação PoC. Comparabilidade entre peers requer revisão.' if metric=='roce' and 'nopat_disclosed' in keys else 'Componentes reais aprovados; regra comum aplicada.')}
