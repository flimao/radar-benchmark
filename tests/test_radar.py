from decimal import Decimal
from radar.domain import calculate, ltm, quarter, ratio

def test_ltm_requires_complete_window():
    assert ltm([1,2,3]) is None
    assert ltm([1,2,None,4]) is None
    assert ltm([1,2,3,4]) == Decimal(10)

def test_ytd_conversion():
    assert quarter(150,100)==50

def test_zero_denominator():
    assert ratio(50,0) is None

def test_cash_bridge_and_lease_sensitivity():
    rows=[dict(cfo=100,capex=30,distribution=20,debt=80,ebitda=40,leases=16)]*4
    result=calculate(rows)
    assert result['cfo']==400
    assert result['fcf']==280
    assert result['residual']==200
    assert result['leverage']==Decimal('.5')
    assert calculate(rows,True)['leverage']==Decimal('.6')
    assert result['roce'] is None

def test_auth_and_export(monkeypatch,tmp_path):
    monkeypatch.setenv('RADAR_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('RADAR_SESSION_SECRET','test-secret')
    from werkzeug.security import generate_password_hash
    monkeypatch.setenv('RADAR_PASSWORD_HASH',generate_password_hash('test-password'))
    from radar.web.app import server
    client=server.test_client()
    assert client.get('/').status_code==302
    assert client.get('/export').status_code==302
    assert client.get('/health').json=={'status':'ok'}
    client.get('/login')
    with client.session_transaction() as sess: csrf=sess['csrf']
    assert client.post('/login',data={'csrf':'wrong','password':'test-password'}).status_code==403
    assert client.post('/login',data={'csrf':csrf,'password':'wrong'}).status_code==200
    assert client.post('/login',data={'csrf':csrf,'password':'test-password'}).status_code==302
    assert client.get('/').status_code==200
    assert client.get('/export').status_code==200

def test_original_idempotency(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    digest,status=data.preserve(b'%PDF-example','test.pdf','Shell','2025Q4','https://example.org','p.1')
    assert status=='REVISAO'
    assert data.preserve(b'%PDF-example','test.pdf','Shell','2025Q4','https://example.org','p.1')[1]=='NO_CHANGE'
    assert (tmp_path/'data/original'/digest).read_bytes()==b'%PDF-example'

def test_pages_and_metric_callbacks(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    from radar.web.app import render, metric_chart, NAV
    for key,_,_ in NAV:
        result=render('/'+key,list(data.COMPANIES),'2025Q4','standard','no')
        assert result[0]
        assert result[2]
    assert metric_chart('cfo',list(data.COMPANIES),'2025Q4','standard','no') is not None

def test_roce_golden_and_leases():
    from radar.domain import roce
    rows=[dict(period=f'2025Q{i}',ebit_adjusted=100,operating_tax=25,
               capital_employed_open=900,capital_employed_close=1100,
               leases_open=100,leases=100) for i in range(1,5)]
    assert roce(rows)==Decimal('30')
    assert roce(rows,True)==Decimal(300)/Decimal(1100)*100
    rows[-1]['operating_tax']=None
    assert roce(rows) is None

def test_roce_unavailable_and_negative_profit():
    from radar.domain import roce
    rows=[dict(period=f'2025Q{i}',ebit_adjusted=-100,operating_tax=-20,
               capital_employed_open=1000,capital_employed_close=1000) for i in range(1,5)]
    assert roce(rows)==Decimal('-32')
    assert roce(rows[:3]) is None
    rows[-1]['period']='2026Q1'
    assert roce(rows) is None
    rows[-1]['period']='2025Q4'
    rows[0]['capital_employed_open']=0
    rows[-1]['capital_employed_close']=0
    assert roce(rows) is None

def test_demo_rates_and_migration(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    frame=data.facts()
    for company,rate in [('Chevron','.10'),('Shell','.20'),('Petrobras','.25'),('Equinor','.25')]:
        row=frame[frame.company==company].iloc[0]
        assert Decimal(str(row.tax_rate))==Decimal(rate)
        assert abs(row.operating_tax-row.ebit_adjusted*float(rate))<0.000001
    assert all(r['roce'] is not None for r in data.metrics('2025Q4',list(data.COMPANIES)))
    assert all(r['roce'] is None for r in data.metrics('2024Q3',list(data.COMPANIES)))
    import duckdb
    with duckdb.connect(str(tmp_path/'database/radar.duckdb')) as db:
        db.execute('UPDATE facts SET ebit_adjusted=NULL')
    data.initialize()
    assert len(data.facts())==64
    data.initialize()
    assert len(data.facts())==64
    assert data.facts()[data.facts().version==1].ebit_adjusted.isna().all()
    assert all(r['roce'] is not None for r in data.metrics('2025Q4',list(data.COMPANIES)))
