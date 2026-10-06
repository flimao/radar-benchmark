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
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    from radar.web import app as web
    server=web.server
    monkeypatch.setattr(web,'PASSWORD_HASH',generate_password_hash('test-password'))
    monkeypatch.setitem(server.config,'SECRET_KEY','test-secret')
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
        result=render('/'+key,list(data.COMPANIES),'2025Q4','standard',[])
        assert result[0]
        assert result[2]
    assert metric_chart('cfo',list(data.COMPANIES),'2025Q4','standard',[]) is not None

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
    for company,rate in [('Chevron','.10'),('Shell','.20'),('Petrobras','.25'),('TotalEnergies','.25')]:
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


def test_non_comparable_preserves_value_and_highlights_chart_point(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    import duckdb
    with duckdb.connect(str(tmp_path/'database/radar.duckdb')) as db:
        db.execute("INSERT INTO metric_assessment VALUES ('Petrobras','2025Q4','roce','standard',1,'NAO_COMPARAVEL','Imposto operacional sem reconstrução defensável')")
    from radar.web.app import metric_cell, metric_chart, cash_table
    row=data.metrics('2025Q4',['Petrobras'])[0]
    cell=metric_cell(row,'roce','standard')
    assert cell.className == 'metric-row'
    assert cell.children[1].children[1].title == 'Imposto operacional sem reconstrução defensável'
    assert '24,7%'==cell.children[1].children[0]
    chart=metric_chart('roce',['Petrobras'],'2025Q4','standard',[])
    figure=chart.children[1].children[0].figure
    assert figure.data[0].y[-1]==row['roce']
    assert figure.data[0].marker.symbol[-1]=='diamond-open'
    assert figure.data[0].customdata is None
    assert 'COMPARÁVEL' not in figure.data[0].hovertemplate
    assert len(chart.children[1].children)==1
    assert 'non-comparable' not in metric_cell(row,'roce','reported').className
    row['quality']['cfo']={'status':'NAO_COMPARAVEL','reason':'Perímetro distinto'}
    cash=cash_table([row])
    cells=cash.children.children[1].children[0].children
    assert cells[1].children.children[1].children == '⚠'
    assert cells[3].children.children[1].title == 'Perímetro distinto'
    assert all(not getattr(cell,'style',None) for cell in cells)
    assert cash.className == 'value-table-container'

def test_goodwill_filter_preserves_other_metrics(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    baseline=data.metrics('2025Q4',['Petrobras'])[0]
    without=data.metrics('2025Q4',['Petrobras'],exclude_goodwill=True)[0]
    assert abs(without['roce']-baseline['roce']/0.9)<1e-8
    for key in ('cfo','leverage','capex','distribution','fcf','residual','reported_roce'):
        assert without[key]==baseline[key]
    from radar.web.app import render, metric_chart
    for option in ([],['include_leases'],['exclude_goodwill'],['include_leases','exclude_goodwill'],None):
        assert render('/trajectory',['Petrobras'],'2025Q4','standard',option)[2]
        chart=metric_chart('roce',['Petrobras'],'2025Q4','standard',option)
        expected=data.metrics('2025Q4',['Petrobras'],'include_leases' in (option or []),'exclude_goodwill' in (option or []))[0]['roce']
        assert chart.children[1].children[0].figure.data[0].y[-1]==expected

def test_driver_figures_follow_company_and_period_filters():
    from radar.web.drivers import figures
    colors={'Petrobras':'#008542','Shell':'#b28700'}
    subset=figures('2025Q2',['Shell'],colors)
    assert subset['brent'].data[0].x[-1]=='2025Q2'
    assert len(subset['brent'].data[0].x)==6
    assert len(subset['margin'].data)==1
    assert subset['margin'].data[0].name=='Shell'
    assert sum(trace.y[0] for trace in subset['gas'].data)==100
    empty=figures('2025Q2',[],colors)
    assert not empty['margin'].data
    assert empty['brent'].data[0].y==subset['brent'].data[0].y

def test_driver_kpi_overlay_axes_and_sensitivities(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    from radar.web.app import driver_charts
    base=driver_charts('none',['Petrobras'],'2025Q4','standard',[])
    overlay=driver_charts('roce',['Petrobras'],'2025Q4','standard',['exclude_goodwill'])
    for index in (0,1,3):
        fig=overlay[0].children[index].children[1].figure
        assert fig.data[-1].yaxis=='y2'
        assert fig.data[-1].line.dash=='dash'
        assert fig.layout.yaxis2.side=='right'
        assert fig.data[-1].y[-1]==data.metrics('2025Q4',['Petrobras'],exclude_goodwill=True)[0]['roce']
        assert len(fig.data)==len(base[0].children[index].children[1].figure.data)+1
    assert len(overlay[0].children[2].children[1].figure.data)==2

def test_peer_replacement_preserves_history_and_seeds_totalenergies(monkeypatch,tmp_path):
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    import duckdb
    with duckdb.connect(str(tmp_path/'database/radar.duckdb')) as db:
        db.execute("UPDATE facts SET company='Equinor' WHERE company='TotalEnergies'")
    data.initialize()
    data.initialize()
    frame=data.facts()
    assert set(frame.company)=={'Petrobras','TotalEnergies','Chevron','Shell'}
    assert len(frame)==32
    peer=frame[frame.company=='TotalEnergies']
    assert len(peer)==8
    assert all(peer.tax_rate==0.25)
    assert data.COMPANIES['TotalEnergies'][1:]==('IFRS','França')
    assert data.SOURCES['TotalEnergies']=='https://totalenergies.com/investors/results'
    with duckdb.connect(str(tmp_path/'database/radar.duckdb')) as db:
        assert db.execute("SELECT count(*) FROM facts WHERE company='Equinor'").fetchone()[0]==8
    assert set(data.export().company)==set(data.COMPANIES)

def test_add_quarter_persisted_without_fabricating_facts(monkeypatch,tmp_path):
    import pytest
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    before=len(data.facts())
    assert data.add_period('2026Q1')
    assert not data.add_period('2026Q1')
    with pytest.raises(ValueError): data.add_period('2026Q5')
    data.initialize()
    assert '2026Q1' in data.periods()
    assert len(data.facts())==before
    for row in data.metrics('2026Q1',list(data.COMPANIES)):
        assert row['roce'] is None
        assert row['cfo'] is None
        assert row['reported_roce'] is None
    from radar.web.app import register_period, refresh_period_options, driver_charts
    result=register_period(1,' 2026q2 ')
    assert '2026Q2' in result[2]
    assert '2026Q2' in refresh_period_options('/upload',result[1])
    assert driver_charts('roce',['TotalEnergies'],'2026Q2','standard',[])


def test_all_comparability_notices_start_collapsed():
    from dash import html
    from radar.web.app import comparability_notice
    long= comparability_notice('⚠ NÃO COMPARÁVEL',html.Ul([html.Li('Motivo longo '*30)]))
    assert isinstance(long,html.Details) and long.open is False
    assert isinstance(long.children[0],html.Summary)
    short=comparability_notice('⚠ NÃO COMPARÁVEL',html.Span('Perímetro distinto'))
    assert isinstance(short,html.Details) and short.open is False


def test_direct_ltm_nopat_is_used_once_and_broad_capex_blocks_jv():
    from radar.domain import roce, calculate
    from decimal import Decimal
    rows=[dict(period=f'2025Q{q}',nopat_ltm=100*q,capital_employed_open=1000,capital_employed_close=1000,ebit_adjusted=None,operating_tax=None,cfo=100,capex=40,distribution=10,debt=50,ebitda=100,leases=0,_capex_method='DISCLOSED_BROAD',jv_organic_contributions=5) for q in (1,2,3,4)]
    assert roce(rows)==Decimal(40)  # latest LTM 400, never sum 100+200+300+400
    result=calculate(rows,include_jv=True)
    assert result['capex'] is None and result['fcf'] is None and result['residual'] is None
    assert result['distribution']==10


def test_compare_uses_only_selected_quarter_ltm(monkeypatch,tmp_path):
    from radar.web.app import metric_chart
    from radar import data
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    result=metric_chart('cfo',['Petrobras','Shell'],'2025Q4','standard',[],pathname='/compare')
    fig=result.children[0].children[1].figure
    expected=data.metrics('2025Q4',['Petrobras','Shell'])
    assert [trace.type for trace in fig.data]==['bar','bar']
    assert [trace.y[0] for trace in fig.data]==[row['cfo'] for row in expected]
    assert [trace.x[0] for trace in fig.data]==['Petrobras','Shell']
    comparison_table=result.children[1].children[1].children
    assert [th.children for th in comparison_table.children[0].children.children]==['Empresa','Valor','Unidade']
    assert len(comparison_table.children[1].children)==2
    assert len(result.children)==2


def test_real_method_hides_synthetic_assumptions(monkeypatch,tmp_path):
    from radar import data
    from radar.web.app import render
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    def visible_text(value):
        if isinstance(value,str):return value
        if isinstance(value,(list,tuple)):return ' '.join(visible_text(v) for v in value)
        return visible_text(getattr(value,'children',None)) if value is not None else ''
    text=visible_text(render('/method',['Shell'],'2025Q4','standard',[],dataset='REAL')).lower()
    assert 'sintét' not in text and 'fictíc' not in text
    demo=visible_text(render('/method',['Shell'],'2025Q4','standard',[])).lower()
    assert 'premissas do roce sintético' in demo


def test_document_links_download_original_filename_and_require_auth(monkeypatch,tmp_path):
    from radar import data
    from radar.web import app as web
    monkeypatch.setattr(data,'ROOT',tmp_path)
    data.initialize()
    digest,_=data.preserve(b'%PDF-example','relatorio (2025).pdf','Shell','2025Q4','https://example.org','p.1')
    grid=web.document_table(data.documents().astype(str).to_dict('records'))
    assert grid.data[0]['filename'].endswith('](/original/'+digest+')')
    assert grid.data[0]['filename'].startswith('[relatorio \\(2025\\)\\.pdf]')
    assert next(c for c in grid.columns if c['id']=='filename')['presentation']=='markdown'
    monkeypatch.setattr(web,'PASSWORD_HASH','configured')
    client=web.server.test_client()
    assert client.get('/original/'+digest).status_code==302
    with client.session_transaction() as session:session['authenticated']=True
    response=client.get('/original/'+digest)
    assert response.status_code==200 and response.data==b'%PDF-example'
    assert 'relatorio (2025).pdf' in response.headers['Content-Disposition']
    assert client.get('/original/'+'0'*64).status_code==404


def test_warning_tooltip_contains_only_justification():
    from radar.web.app import warning_icon
    icon=warning_icon('Aproximação do imposto; NÃO COMPARÁVEL.; Capital reconstruído; NÃO-COMPARÁVEL')
    assert icon.title=='Aproximação do imposto; Capital reconstruído'
    assert icon.children=='⚠'
