import copy
import hashlib
import json
from decimal import Decimal

import httpx
import pytest
from radar import data
from radar.ingestion import pipeline as pipe
from radar.ingestion.extract import number, extract
from radar.ingestion.sources import download, fetch_ptax, fetch_yahoo


@pytest.fixture
def prepared(monkeypatch,tmp_path):
    monkeypatch.setattr(data,'ROOT',tmp_path)
    content='id,value\nq1,100\nq2,250\nq3,400\nq4,600\nref,600\nwrong,700\nzero,0\n'
    (tmp_path/'source.csv').write_text(content)
    manifest={'schema_version':1,'company':'Shell','accounting_standard':'IFRS','mapping_version':'test-v1','mapping_note':'Test fixture',
              'documents':[{'id':'doc','format':'csv','path':'source.csv','url':'https://www.shell.com/source.csv'}],
              'observations':[]}
    for quarter in range(1,5):
        manifest['observations'].append({'id':f'q{quarter}','field':'cfo','concept':'STATUTORY_CFO','period':f'2025Q{quarter}',
            'document':'doc','currency':'USD','scale':'millions','basis':'REPORTED','scope':'CONSOLIDATED','period_type':'YTD',
            'selector':{'where':{'id':f'q{quarter}'},'column':'value'}})
    return tmp_path,manifest


def test_number_sign_locale_and_absence():
    assert number('(1,234.50)')==Decimal('-1234.50')
    assert number('1.234,50','pt')==Decimal('1234.50')
    assert number('-',dash_zero=True)==0
    for value in (None,True,'NaN','Infinity','-'):
        with pytest.raises(ValueError):number(value)


def test_ytd_quarter_publication_idempotency_and_no_demo_mix(prepared):
    root,manifest=prepared
    batch=pipe.stage(manifest,base_dir=root)
    assert [Decimal(p['value']) for p in batch['report']['points']]==[100,150,150,200]
    assert batch['report']['points'][-1]['flags']==['DERIVED_QUARTER','VARIATION_ALERT']
    assert pipe.stage(manifest,base_dir=root)['id']==batch['id']
    with pytest.raises(ValueError):pipe.publish(batch['id'])
    assert data.facts('REAL').empty
    reviewed=pipe.approve(batch['id'],'Test reviewer','Synthetic test fixture only',accept_alerts=True)
    assert reviewed['status']=='APROVADO'
    pipe.publish(batch['id']);pipe.publish(batch['id'])
    result=data.metrics('2025Q4',['Shell','Chevron'],dataset='REAL')
    assert result[0]['cfo']==600 and result[0]['fcf'] is None
    assert result[1]['cfo'] is None
    assert len(data.facts('REAL'))==4
    assert len(data.facts())==32
    assert result[0]['quality']['roce']['status']=='NAO_COMPARAVEL'
    with pytest.raises(ValueError):pipe.approve(batch['id'],'Test','Cannot mutate')


def test_missing_predecessor_does_not_publish_ytd_as_quarter(prepared):
    root,manifest=prepared
    manifest['observations']=manifest['observations'][1:]
    points=pipe.stage(manifest,base_dir=root)['report']['points']
    assert points[0]['value'] is None and points[0]['state']=='BLOQUEADO'


def test_nonofficial_source_cannot_be_approved(prepared):
    root,manifest=prepared
    manifest['documents'][0]['url']='https://example.org/source.csv'
    batch=pipe.stage(manifest,base_dir=root)
    assert all(p['state']=='BLOQUEADO' for p in batch['report']['points'])
    with pytest.raises(ValueError):pipe.approve(batch['id'],'Test','Invalid source',accept_alerts=True)


def test_noncomparable_cfo_preserves_value_and_excludes_comparison(prepared):
    root,manifest=prepared
    for o in manifest['observations']:o['concept']='CFO_EX_WORKING_CAPITAL'
    batch=pipe.stage(manifest,base_dir=root)
    pipe.approve(batch['id'],'Test','Concept exception accepted for display',accept_alerts=True)
    pipe.publish(batch['id'])
    row=data.metrics('2025Q4',['Shell'],dataset='REAL')[0]
    assert row['cfo']==600 and row['quality']['cfo']['status']=='NAO_COMPARAVEL'


def test_reconciliation_blocks_bad_bridge_and_unrelated_bridge(prepared):
    root,manifest=prepared
    manifest['observations']=manifest['observations'][:1]
    reference={**manifest['observations'][0],'id':'ref','field':None,'selector':{'where':{'id':'wrong'},'column':'value'}}
    manifest['observations'].append(reference)
    manifest['reconciliations']=[{'id':'bridge','reference':'ref','terms':[{'observation':'q1','coefficient':1}],'applies_to':['q1'],'reason':'Independent source control'}]
    batch=pipe.stage(manifest,base_dir=root)
    assert not batch['report']['reconciliations'][0]['passed']
    with pytest.raises(ValueError):pipe.approve(batch['id'],'Test','Cannot bypass reconciliation',accept_alerts=True)
    manifest['reconciliations'][0]['terms']=[{'observation':'q1','coefficient':7}]
    batch=pipe.stage(manifest,base_dir=root)
    assert not batch['report']['reconciliations'][0]['passed']
    assert 'não corresponde' in batch['report']['reconciliations'][0]['error']


def test_real_tax_no_synthetic_rate_and_adjustment_set_required(prepared):
    root,manifest=prepared
    tax=manifest['observations'][0]
    tax.update(field='operating_tax',concept='OPERATING_TAX',tax_method='ESTIMATED',adjustment_set='A')
    manifest['observations']=[tax]
    with pytest.raises(ValueError,match='Alíquota sintética'):pipe.stage(manifest,base_dir=root)


def test_brl_converts_derived_quarter_then_ltm(prepared):
    root,manifest=prepared
    payload={'value':[{'dataHoraCotacao':f'2025-{m:02d}-15 13:00:00','tipoBoletim':'Fechamento','cotacaoVenda':rate} for m,rate in [(1,4),(2,6),(3,5),(4,10),(5,10),(6,10),(7,5),(8,5),(9,5),(10,4),(11,4),(12,4)]]}
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=payload)))
    snapshot=pipe.save_snapshot(fetch_ptax('2025-01-01','2025-12-31',client=client))
    for o in manifest['observations']:o['currency']='BRL'
    manifest['fx']=snapshot['hash']
    batch=pipe.stage(manifest,base_dir=root)
    assert [Decimal(p['value']) for p in batch['report']['points']]==[20,15,30,50]
    pipe.approve(batch['id'],'Test','FX conversion fixture',accept_alerts=True);pipe.publish(batch['id'])
    assert data.metrics('2025Q4',['Shell'],dataset='REAL')[0]['cfo']==115


def test_download_rejects_redirect_and_size():
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(302,headers={'location':'http://127.0.0.1/'})))
    with pytest.raises(ValueError,match='Redirecionamento'):download('https://www.shell.com/file','Shell',client=client)
    with pytest.raises(ValueError):download('https://www.shell.com.evil.org/file','Shell')
    with pytest.raises(ValueError):download('https://www.shell.com:8443/file','Shell')


def test_ptax_filters_closing_quotes_and_rejects_duplicates(prepared):
    payload={'value':[{'dataHoraCotacao':'2025-01-02 13:00:00','tipoBoletim':'Fechamento','cotacaoVenda':5},
                      {'dataHoraCotacao':'2025-01-02 10:00:00','tipoBoletim':'Abertura','cotacaoVenda':4}]}
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=payload)))
    assert fetch_ptax('2025-01-01','2025-03-31',client=client)['rates']=={'2025-01-02':'5'}
    payload['value'].append({**payload['value'][0],'cotacaoVenda':6})
    with pytest.raises(ValueError,match='duplicada'):fetch_ptax('2025-01-01','2025-03-31',client=client)


def test_yahoo_only_context_and_nulls(prepared):
    payload={'chart':{'error':None,'result':[{'meta':{'currency':'USD','exchangeTimezoneName':'UTC'},'timestamp':[1735776000,1735862400],
                                           'indicators':{'quote':[{'close':[75,None]}]}}]}}
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=payload)))
    result=fetch_yahoo('BZ=F','2025-01-01','2025-01-31',client=client)
    assert result['usage']=='CONTEXTO' and len(result['points'])==1
    assert result['points'][0]['close']=='75'


def test_restatements_keep_history_and_latest_approved_version(prepared):
    root,manifest=prepared
    batch=pipe.stage(manifest,base_dir=root);pipe.approve(batch['id'],'Test','Version 1',accept_alerts=True);pipe.publish(batch['id'])
    path=root/'source.csv';path.write_text(path.read_text().replace('q4,600','q4,650'))
    manifest['mapping_version']='test-v2'
    revision=pipe.stage(manifest,base_dir=root)
    assert revision['id']!=batch['id']
    assert data.metrics('2025Q4',['Shell'],dataset='REAL')[0]['cfo']==600
    pipe.approve(revision['id'],'Test','Revision documented',accept_alerts=True);pipe.publish(revision['id'])
    assert data.metrics('2025Q4',['Shell'],dataset='REAL')[0]['cfo']==650
    assert len(pipe.batches())==2


def test_duplicate_keys_and_wrong_accounting_standard(prepared):
    root,manifest=prepared
    manifest['accounting_standard']='US GAAP'
    with pytest.raises(ValueError):pipe.stage(manifest,base_dir=root)
    manifest['accounting_standard']='IFRS';manifest['observations'][1]['period']='2025Q1'
    with pytest.raises(ValueError,match='duplicado'):pipe.stage(manifest,base_dir=root)


def test_xbrl_filing_selection_ambiguity_and_identity(tmp_path):
    file=tmp_path/'sec.json'
    facts={'cik':93410,'facts':{'us-gaap':{'NetCashProvidedByUsedInOperatingActivities':{'units':{'USD':[
        {'start':'2025-01-01','end':'2025-03-31','val':100000000,'accn':'A','form':'10-Q'},
        {'start':'2025-01-01','end':'2025-03-31','val':120000000,'accn':'B','form':'10-Q'}]}}}}}
    file.write_text(json.dumps(facts))
    selector={'taxonomy':'us-gaap','tag':'NetCashProvidedByUsedInOperatingActivities','unit':'USD','where':{'start':'2025-01-01','end':'2025-03-31'},'guards':[{'path':['cik'],'equals':93410}]}
    with pytest.raises(ValueError,match='exatamente um'):extract(file,'json',selector)
    selector['where']['accn']='B'
    value,locator=extract(file,'json',selector)
    assert value==120000000 and 'accession B' in locator
    selector['guards'][0]['equals']=1
    with pytest.raises(ValueError,match='Identidade'):extract(file,'json',selector)


def test_hybrid_total_equity_nci_leases_and_roce_golden(prepared):
    root,manifest=prepared
    source=root/'source.csv'
    values={'equity_total':1000,'nci':100,'financial_debt_short':100,'financial_debt_long':300,'cash':50,'cash_nonoperating':0,
            'leases':100,'goodwill':200,'ebit_adjusted':100,'dda_adjusted':40,'operating_tax':20,'capex':30,'dividends_paid':10,'buybacks':5,'cfo':200}
    # Explicit fixture, not real financial approval. Total equity includes NCI;
    # debt includes leases; zero cash non-operating is a documented source value.
    source.write_text('id,value\n'+''.join(f'{k},{v}\n{k}-ref,{v}\n' for k,v in values.items()))
    manifest['observations']=[];manifest['reconciliations']=[]
    for period in ['2024Q4']+[f'2025Q{q}' for q in range(1,5)]:
        for field,value in values.items():
            if period=='2024Q4' and field in pipe.FLOW:continue
            id=period+'-'+field
            o={'id':id,'field':field,'concept':next(iter(pipe.CONCEPTS[field])),'period':period,'document':'doc','currency':'USD','scale':'millions','basis':'REPORTED','scope':'CONSOLIDATED',
               'period_type':'BALANCE' if field in pipe.BALANCE else 'QUARTER','selector':{'where':{'id':field},'column':'value'}}
            if field=='cfo':o['concept']='STATUTORY_CFO'
            if field=='capex':o['concept']='ORGANIC_CASH_CAPEX'
            if field.startswith('financial_debt'):o['includes_leases']=True
            if field in ('ebit_adjusted','dda_adjusted','operating_tax'):
                o['adjustment_set']='same-adjustments'
                if field=='operating_tax':o['tax_method']='DISCLOSED'
                ref={**o,'id':id+'-ref','field':None,'selector':{'where':{'id':field+'-ref'},'column':'value'}}
                manifest['observations'].append(ref)
                manifest['reconciliations'].append({'id':id+'-bridge','reference':id+'-ref','terms':[{'observation':id,'coefficient':1}],'applies_to':[id],'reason':'Independent fixture control'})
            manifest['observations'].append(o)
    batch=pipe.stage(manifest,base_dir=root)
    pipe.approve(batch['id'],'Test','Golden financial fixture');pipe.publish(batch['id'])
    base=data.metrics('2025Q4',['Shell'],dataset='REAL')[0]
    assert base['cfo']==800 and base['fcf']==680 and base['residual']==620
    assert base['leverage']==pytest.approx(250/560)
    # Equity total 1000 + debt excluding leases 300 = CE 1300 (no extra NCI).
    assert base['roce']==pytest.approx(320/1300*100)
    assert data.metrics('2025Q4',['Shell'],leases=True,dataset='REAL')[0]['roce']==pytest.approx(320/1400*100)
    assert data.metrics('2025Q4',['Shell'],exclude_goodwill=True,dataset='REAL')[0]['roce']==pytest.approx(320/1100*100)
    assert base['quality']['roce']['status']=='COMPARAVEL'


def test_real_pages_do_not_reuse_demo_drivers(prepared):
    root,manifest=prepared
    pipe.initialize()
    from radar.web.app import render,metric_chart,driver_charts,dataset_labels
    for path in ['/','/trajectory','/cash','/quality','/upload']:
        assert render(path,['Shell'],'2025Q4','standard',[],'REAL')[0]
    chart=metric_chart('cfo',['Shell'],'2025Q4','standard',[],'REAL')
    assert all(y is None for y in chart.children[1].children[0].figure.data[0].y)
    figures=driver_charts('none',['Shell'],'2025Q4','standard',[],'REAL')
    assert 'dataset=REAL' in dataset_labels('REAL')[2]
    assert 'Yahoo' in figures[0].children[0].children[0].children[0].children


def test_xlsx_guard_missing_cache_and_pdf_ambiguous_label(tmp_path):
    from openpyxl import Workbook
    import pymupdf
    book=Workbook();sheet=book.active;sheet.title='Results'
    sheet['A1']='2025Q1';sheet['B1']=123;sheet['C1']='=B1*2'
    file=tmp_path/'fixture.xlsx';book.save(file)
    selector={'sheet':'Results','cell':'B1','guards':[{'cell':'A1','equals':'2025Q1'}]}
    assert extract(file,'xlsx',selector)==(123,'Results!B1')
    selector['guards'][0]['equals']='2025Q2'
    with pytest.raises(ValueError,match='Cabeçalho'):extract(file,'xlsx',selector)
    selector['guards'][0]['equals']='2025Q1';selector['cell']='C1'
    with pytest.raises(ValueError,match='sem valor calculado'):extract(file,'xlsx',selector)
    pdf=pymupdf.open();page=pdf.new_page();page.insert_text((72,72),'Label\n100\nLabel\n200')
    file=tmp_path/'fixture.pdf';pdf.save(file);pdf.close()
    selector={'page':1,'label':'Label','column':0}
    with pytest.raises(ValueError,match='ambíguo'):extract(file,'pdf',selector)
    selector['occurrence']=1
    assert extract(file,'pdf',selector)[0]=='200'


def test_balance_ptax_previous_publication_and_no_future(prepared):
    root,manifest=prepared
    p=manifest['observations'][0]
    p.update(field='goodwill',concept='GOODWILL',period_type='BALANCE',currency='BRL')
    manifest['observations']=[p]
    payload={'value':[{'dataHoraCotacao':'2025-03-28 13:00:00','tipoBoletim':'Fechamento','cotacaoVenda':5}]}
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=payload)))
    manifest['fx']=pipe.save_snapshot(fetch_ptax('2025-01-01','2025-03-31',client=client))['hash']
    point=pipe.stage(manifest,base_dir=root)['report']['points'][0]
    assert point['value']=='20' and point['fx_date']=='2025-03-28' and point['fx_fallback']
    p['period']='2024Q4'
    point=pipe.stage(manifest,base_dir=root)['report']['points'][0]
    assert point['state']=='BLOQUEADO' and point['value'] is None


def test_api_sec_contact_and_issuer_validation(prepared,monkeypatch):
    from radar.ingestion.sources import fetch_sec_companyfacts
    payload={'cik':93410,'entityName':'CHEVRON CORP','facts':{'us-gaap':{'Cash':{}}}}
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=payload)))
    monkeypatch.delenv('RADAR_SEC_USER_AGENT',raising=False)
    with pytest.raises(ValueError,match='USER_AGENT'):fetch_sec_companyfacts('Chevron','93410',client=client)
    monkeypatch.setenv('RADAR_SEC_USER_AGENT','RADAR Test tests@example.org')
    assert fetch_sec_companyfacts('Chevron','93410',client=client)['entity_name']=='CHEVRON CORP'
    payload['cik']=1
    with pytest.raises(ValueError,match='emissor'):fetch_sec_companyfacts('Chevron','93410',client=client)


def test_cash_distributions_sign_and_mapping_pending(prepared):
    root,manifest=prepared
    (root/'source.csv').write_text('id,value\nq1,(1851)\nq2,(1894)\nq3,(2216)\nq4,(2160)\nannual,(8121)\n')
    for o in manifest['observations']:
        o.update(field='dividends_paid',concept='DIVIDENDS_PAID',period_type='QUARTER',sign=-1)
    reference=copy.deepcopy(manifest['observations'][-1])
    reference.update(id='annual',period_type='YTD');reference.pop('field');reference.pop('concept')
    reference['selector']['where']['id']='annual'
    manifest['observations'].append(reference)
    manifest['reconciliations']=[dict(id='annual',reference='annual',aggregation='SUM_QUARTERS',terms=[dict(observation=f'q{q}',coefficient=1) for q in range(1,5)],applies_to=[f'q{q}' for q in range(1,5)],reason='Dividendos pagos: DFC trimestral versus anual.')]
    manifest['pending_components']=[dict(indicator='ROCE',reason='Imposto operacional pendente')]
    result=pipe.stage(manifest,base_dir=root)['report']
    assert result['errors']==[]
    assert sum(Decimal(p['value']) for p in result['points'])==Decimal('8121')
    assert result['reconciliations'][0]['passed']
    assert result['pending_components']==manifest['pending_components']


def test_disclosed_nopat_alternative_no_fabricated_tax():
    from radar.domain import roce
    rows=[dict(period=f'2025Q{i+1}',nopat_disclosed=n,capital_employed_open=138051,capital_employed_close=142427) for i,n in enumerate([4661,4145,4579,4442])]
    assert abs(roce(rows)-Decimal('12.7118704497'))<Decimal('0.000000001')
    assert all('ebit_adjusted' not in r and 'operating_tax' not in r for r in rows)
    rows[2]['nopat_disclosed']=None
    assert roce(rows) is None


def test_jv_sensitivity_changes_cash_metrics_and_requires_complete_flows():
    from radar.domain import calculate
    from radar.ingestion.financials import quality
    rows=[dict(period=f'2025Q{q}',cfo=100,capex=40,distribution=10,debt=80,ebitda=20,jv_organic_contributions=5,_scope={'capex':'CONSOLIDATED','jv_organic_contributions':'CONSOLIDATED'}) for q in range(1,5)]
    base=calculate(rows);sensitivity=calculate(rows,include_jv=True)
    assert sensitivity['capex']==45
    assert sensitivity['fcf']==220 and sensitivity['residual']==180
    assert sensitivity['leverage']==base['leverage']
    assert sensitivity['cfo']==base['cfo'] and sensitivity['distribution']==base['distribution']
    assert quality(rows,'capex',include_jv=True)['status']=='COMPARAVEL'
    rows[0].pop('jv_organic_contributions')
    assert calculate(rows,include_jv=True)['capex'] is None
    assert quality(rows,'capex',include_jv=True)['status']=='INDISPONIVEL'
    assert calculate(rows)['capex']==40


def test_ebitda_alternative_warning_survives_dataframe(monkeypatch):
    from radar.ingestion import financials
    records=[dict(company='TotalEnergies',period=f'2025Q{q}',version=1,mode='REAL',debt=100,ebitda=20,_quality={},_scope={},_ebitda_method='DISCLOSED_ALTERNATIVE') for q in range(1,5)]
    monkeypatch.setattr(financials,'rows',lambda:records)
    window=financials.facts().to_dict('records')
    assert financials.quality(window,'leverage')['status']=='NAO_COMPARAVEL'
    assert 'Alternativa aprovada' in financials.quality(window,'leverage')['reason']


def test_petrobras_provider_is_scoped_to_issuer():
    from radar.ingestion.sources import official, permitted
    url='https://api.mziq.com/mzfilemanager/v2/d/25fdf098-34f5-4608-b7fa-17d60b2de47d/document?origin=2'
    assert official(url,'Petrobras') and permitted(url,'Petrobras')
    assert not official(url,'Shell')
    assert not official(url.replace('25fdf098-34f5-4608-b7fa-17d60b2de47d','another-company'),'Petrobras')
    assert not official(url.replace('api.mziq.com','api.mziq.com.evil.org'),'Petrobras')


def test_component_reference_bridge_checks_independence_and_basis(prepared):
    root,m=prepared
    m['observations']=m['observations'][:1]
    m['observations'][0]['basis']='RECONSTRUCTED'
    for name,value_id in [('ref','q2'),('deduction','q1')]:
        o=copy.deepcopy(m['observations'][0]);o.pop('field');o['id']=name
        o['selector']={'where':{'id':value_id},'column':'value'};m['observations'].append(o)
    bridge={'id':'multi','reference_terms':[{'observation':'ref','coefficient':1},{'observation':'deduction','coefficient':-1.5}],
        'terms':[{'observation':'q1','coefficient':1}],'applies_to':['q1'],'reason':'Independent component bridge'}
    m['reconciliations']=[bridge]
    b=pipe.stage(m,base_dir=root)
    assert b['report']['reconciliations'][0]['passed']
    m['observations'][-1]['scope']='PARENT'
    b=pipe.stage(m,base_dir=root)
    assert not b['report']['reconciliations'][0]['passed']
    m['observations'][-1]['scope']='CONSOLIDATED';bridge['reference_terms'][1]['observation']='q1'
    b=pipe.stage(m,base_dir=root)
    assert 'independente' in b['report']['reconciliations'][0]['error']

def test_petrobras_normalized_tax_preserves_net_affiliates(monkeypatch):
    from radar.ingestion import financials
    from radar import data
    from decimal import Decimal
    points=[dict(company='Petrobras',period='2025Q1',field=f,value=Decimal(v),comparable=True,reason='',details={'scope':'CONSOLIDATED','adjustment_set':'same'}) for f,v in [('ebit_adjusted','100'),('affiliates_net','10')]]
    monkeypatch.setattr(financials,'published_points',lambda:points)
    row=financials.rows()[0]
    assert row['operating_tax']==Decimal('30.60')
    assert row['ebit_adjusted']-row['operating_tax']==Decimal('69.40')
    assert row['_quality']['operating_tax']['status']=='NAO_COMPARAVEL'
    points[1]['details']['scope']='PARENT'
    assert financials.rows()[0]['operating_tax'] is None
    points[1]['details']['scope']='CONSOLIDATED'
    for p in points:p['company']='Shell'
    assert financials.rows()[0]['operating_tax'] is None

def test_official_html_numeric_selector_rejects_changed_or_ambiguous_values(tmp_path):
    from radar.ingestion.extract import extract
    import pytest
    p=tmp_path/'source.html'
    p.write_text('<p>Petrobras 80% preço R$ 123,00</p><p>preço R$ 123,00</p>')
    sel={'guards':['Petrobras 80%'],'pattern':r'preço R\$ ([\d,]+)'}
    with pytest.raises(ValueError,match='ambíguo'):extract(p,'html',sel)
    sel['allow_identical_duplicates']=True
    assert extract(p,'html',sel)[0]=='123,00'
    p.write_text('<p>Petrobras 80% preço R$ 123,00 preço R$ 456,00</p>')
    with pytest.raises(ValueError,match='ambíguo'):extract(p,'html',sel)
    sel['guards']=['Petrobras 73,24%']
    with pytest.raises(ValueError,match='Contexto'):extract(p,'html',sel)
