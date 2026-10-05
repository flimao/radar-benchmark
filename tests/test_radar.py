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
