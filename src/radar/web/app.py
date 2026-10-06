import base64, io, json, os, re, secrets, time
from pathlib import Path
from collections import defaultdict
from flask import Flask, session, request, redirect, Response, send_file, abort
from werkzeug.security import check_password_hash
from dash import Dash, html, dcc, Input, Output, State, dash_table, no_update
import plotly.graph_objects as go
from radar import data
from radar.web.drivers import figures as driver_figures, real_figures
ROOT=Path(os.environ.get('RADAR_PROJECT_DIR', '.')).resolve()
RULES=json.loads((ROOT/'config/rules.json').read_text())
server=Flask(__name__)
server.secret_key=os.environ.get('RADAR_SESSION_SECRET') or secrets.token_hex(32)
server.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=os.environ.get('RADAR_HTTPS')=='1',MAX_CONTENT_LENGTH=20*1024*1024)
PASSWORD_HASH=os.environ.get('RADAR_PASSWORD_HASH')
if PASSWORD_HASH and not os.environ.get('RADAR_SESSION_SECRET'): raise RuntimeError('RADAR_SESSION_SECRET obrigatório com senha configurada')
# No configured credentials means explicit local demonstration mode.
if not PASSWORD_HASH and os.environ.get('RADAR_ENV')=='production': raise RuntimeError('Configure RADAR_PASSWORD_HASH em produção')
ATTEMPTS=defaultdict(list)
data.initialize()

@server.before_request
def protect():
    if request.path in ('/health','/login'): return
    if PASSWORD_HASH and not session.get('authenticated'): return redirect('/login')

@server.after_request
def headers(response):
    response.headers['X-Robots-Tag']='noindex, nofollow'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='SAMEORIGIN'
    return response

@server.route('/health')
def health(): return {'status':'ok'}

@server.route('/login',methods=['GET','POST'])
def login():
    session.setdefault('csrf',secrets.token_hex(24)); error=''
    if request.method=='POST':
        ip=request.remote_addr; now=time.time(); ATTEMPTS[ip]=[t for t in ATTEMPTS[ip] if now-t<300]
        if len(ATTEMPTS[ip])>=5: return 'Tente novamente em 5 minutos.',429
        if not secrets.compare_digest(request.form.get('csrf',''),session['csrf']): abort(403)
        ATTEMPTS[ip].append(now)
        if PASSWORD_HASH and check_password_hash(PASSWORD_HASH,request.form.get('password','')):
            session.clear(); session['authenticated']=True; return redirect('/')
        error='Senha inválida'
    return f'''<!doctype html><html lang="pt-BR"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="/assets/style.css"><title>Acesso · RADAR</title><body class="login"><form method="post"><div class="brand">◉ RADAR</div><h1>Inteligência com perspectiva.</h1><p>Entre para consultar o benchmarking.</p><input type="hidden" name="csrf" value="{session['csrf']}"><label>Senha compartilhada<input name="password" type="password" required autocomplete="current-password"></label><p role="alert">{error}</p><button>Entrar →</button></form></body></html>'''

@server.route('/export')
def export():
    frame=data.export(request.args.get("dataset","DEMONSTRACAO")); return Response(frame.to_csv(index=False),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=radar-'+('real' if request.args.get('dataset')=='REAL' else 'demonstracao')+'.csv'})

@server.route('/original/<digest>')
def original(digest):
    if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest): abort(404)
    path=data.ROOT/'data/original'/digest
    if not path.exists(): abort(404)
    docs=data.documents()
    matching=docs[docs['hash']==digest]
    filename=Path(str(matching.iloc[0]['filename'])).name if not matching.empty else digest
    return send_file(path,as_attachment=True,download_name=filename)

app=Dash(__name__,server=server,title='RADAR · Benchmarking de energia',assets_folder=str(Path(__file__).parent/'assets'),suppress_callback_exceptions=True)
NAV=[('overview','◫','Resumo executivo'),('trajectory','↗','Posição e trajetória'),('compare','≋','Comparação por KPI'),('drivers','◎','Drivers e contexto'),('cash','⇄','Ponte de caixa'),('quality','◇','Qualidade dos dados'),('method','▤','Metodologia e fontes'),('rules','⤺','Regras e revisões'),('admin','⊕','Administração de carga')]
def badge(text,kind=''): return html.Span(text,className='badge '+kind)
def panel(title,children,subtitle=None): return html.Section([html.Div([html.H3(title),html.P(subtitle) if subtitle else None],className='panel-head'),children],className='panel')
def graph(fig, height=300):
    fig.update_layout(template='plotly_white',font=dict(family='system-ui',color='#53615b',size=12),margin=dict(l=45,r=24,t=20,b=38),paper_bgcolor='white',plot_bgcolor='white',legend=dict(orientation='h',y=1.12,x=0),height=height)
    fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor='#edf1ee',zerolinecolor='#edf1ee')
    if height > 300:
        fig.update_layout(margin=dict(l=85,r=30,t=65,b=75),legend=dict(orientation='h',y=1.12,x=0))
        fig.update_yaxes(automargin=True,nticks=6,title_standoff=18)
        fig.update_xaxes(automargin=True,tickangle=-30)
    return dcc.Graph(style={'height':f'{height}px'},figure=fig,config={'displayModeBar':False,'responsive':True})
def table(rows, column_labels=None, flagged_cells=None):
    if not rows: return html.P('Nenhum registro disponível.',className='empty')
    return dash_table.DataTable(data=rows,columns=[{'name':(column_labels or {}).get(k,k.replace('_',' ').capitalize()),'id':k} for k in rows[0]],style_table={'overflowX':'auto'},style_cell={'fontFamily':'system-ui','textAlign':'left','padding':'16px','fontSize':13,'border':'none','color':'#344b40'},style_header={'backgroundColor':'#f5f8f6','fontWeight':600,'border':'none'},style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'#fafcfb'}]+[{'if':{'row_index':index,'column_id':key},'backgroundColor':'#fff0e8','color':'#852800','fontWeight':'bold','border':'2px solid #a33b0a','whiteSpace':'pre-line'} for index,key in (flagged_cells or [])],page_size=12)
app.layout=html.Div([
    dcc.Location(id='location'),dcc.Store(id='period-revision'),
    html.A('Ir para o conteúdo',href='#content',className='skip'),
    html.Aside([html.A([html.Span('◉',className='brand-icon'),'RADAR',html.Span('ENERGY INTELLIGENCE',className='brand-caption')],href='/',className='brand'),html.Div('WORKSPACE',className='nav-label'),html.Nav([html.A([html.Span(icon,className='nav-icon'),label],href='/' if key=='overview' else '/'+key,id='nav-'+key,className='nav-link') for key,icon,label in NAV]),html.Div([html.Div('RESILIÊNCIA QUE GERA VALOR',className='sidebar-note'),html.P('Uma visão comparável.\nDecisões com contexto.'),html.Div([html.Span('●',className='green-dot'),' PoC de benchmarking'],className='environment')],className='sidebar-footer')],className='sidebar'),
    html.Div([html.Header([html.Div([html.Span('Benchmarking financeiro',className='breadcrumb'),html.Span(' / '),html.Span('Óleo e gás')]),html.Div([html.Span(id='dataset-badge'),html.Span('PT-BR',className='locale'),html.Div('RA',className='avatar')],className='header-actions')],className='topbar'),
    html.Main([html.Div([html.Div([html.Div('INTELIGÊNCIA PARA DECISÃO',className='eyebrow'),html.H1(id='page-title'),html.P(id='page-description',className='page-description')]),html.A(['↓  Exportar dados'],href='/export',id='export-link',className='button secondary')],className='page-heading'),
    html.Div([html.Div([html.Label('BASE DE DADOS'),dcc.Dropdown([{'label':'Demonstração','value':'DEMONSTRACAO'},{'label':'Reais · aprovados','value':'REAL'}],'DEMONSTRACAO',id='dataset',clearable=False,persistence=True,persistence_type='session')],className='filter'),html.Div([html.Label('EMPRESAS'),dcc.Dropdown(list(data.COMPANIES),list(data.COMPANIES),multi=True,id='companies',persistence='peers-totalenergies-v1',persistence_type='session',clearable=False)],className='filter companies'),html.Div([html.Label('TRIMESTRE DE REFERÊNCIA'),dcc.Dropdown(data.periods(),'2025Q4',id='period',persistence=True,persistence_type='session',clearable=False)],className='filter'),html.Div([html.Label('VISÃO DOS INDICADORES'),dcc.Dropdown([{'label':'Padronizado · LTM','value':'standard'},{'label':'Reportado · ROCE','value':'reported'}],'standard',id='view',persistence=True,persistence_type='session',clearable=False)],className='filter'),html.Div([html.Label('SENSIBILIDADES'),dcc.Dropdown([{'label':'Incluir leases','value':'include_leases'},{'label':'Excluir goodwill','value':'exclude_goodwill'},{'label':'Incluir aportes orgânicos em JVs','value':'include_jv'}],[],id='sensitivities',persistence=True,persistence_type='session',multi=True,clearable=True,placeholder='Base: sem leases, com goodwill'),html.Small('Base sem leases, com goodwill e sem aportes em JVs',className='sensitivity-hint')],className='filter')],className='filters'),
    html.Div(id='dataset-notice',className='demo-notice'),html.Div(id='page-content'),html.Footer([html.Span('RADAR  /  Resiliência que gera valor'),html.Span(f"USD · regras v{RULES['version']} · nenhuma recomendação de investimento")])],id='content')],className='workspace')],className='shell')

@app.callback(Output('page-title','children'),Output('page-description','children'),Output('page-content','children'),*[Output('nav-'+key,'className') for key,_,_ in NAV],Input('location','pathname'),Input('companies','value'),Input('period','value'),Input('view','value'),Input('sensitivities','value'),Input('dataset','value'))
def render(path,companies,period,view,sensitivities,dataset="DEMONSTRACAO"):
    key=(path or '/').strip('/') or 'overview'; key=key if key in [n[0] for n in NAV] else 'overview'
    title=next(n[2] for n in NAV if n[0]==key); rows=data.metrics(period,companies or [],'include_leases' in (sensitivities or []),exclude_goodwill='exclude_goodwill' in (sensitivities or []),dataset=dataset,include_jv='include_jv' in (sensitivities or [])); df=data.facts(dataset); colors={c:v[0] for c,v in data.COMPANIES.items()}
    content=[]
    if key=='overview':
        descriptions=[('4','Empresas no radar','IFRS e US GAAP'),(str(df.period.nunique()),'Trimestres disponíveis','Dados reais publicados' if dataset=='REAL' else 'Histórico demonstrativo'),('5','Indicadores essenciais','Retorno, caixa e disciplina'),('LTM','Perspectiva de análise','Quatro trimestres completos')]
        content.append(html.Div([html.Div([html.Div(label,className='stat-label'),html.Div(value,className='stat-value'),html.Div(note,className='stat-note')],className='stat') for value,label,note in descriptions],className='stats'))
        content.append(html.Div([html.Div([badge('PANORAMA DO SETOR'),html.H2(['Resiliência que',html.Br(),'gera valor.']),html.P('Observe a capacidade de gerar caixa, sustentar investimentos e remunerar acionistas ao longo do ciclo.'),html.A('Explorar a trajetória  ↗',href='/trajectory',className='hero-link')],className='hero'),panel('Geração e alocação de caixa',cash_chart(rows,colors),'Fluxos LTM · US$ bilhões · '+('reais aprovados' if dataset=='REAL' else 'dados demonstrativos'))],className='overview-grid'))
        content.append(panel('As empresas, lado a lado',comparison(rows,view),'Perspectivas complementares, sem ranking composto. Clique em uma empresa para consultar as definições.'))
        content.append(html.Div([panel('Uma leitura em cinco etapas',html.Div([html.Span(x) for x in ['01  Posição','02  Trajetória','03  Resiliência','04  Geração de valor','05  Decisão']],className='journey')),panel('Transparência em cada indicador',html.Div([badge('REAIS APROVADOS' if dataset=='REAL' else 'DEMONSTRAÇÃO','warning'),html.P('A base real usa somente componentes aprovados. Ausências permanecem indisponíveis; imposto operacional exige divulgação ou reconstrução defensável.' if dataset=='REAL' else 'ROCE calculado com componentes sintéticos e alíquotas fictícias: Chevron 10%, Shell 20%, Petrobras e TotalEnergies 25%. Os valores reportados do exemplo são sintéticos.'),html.A('Consultar metodologia  →',href='/method')]))],className='two-col'))
    elif key in ('trajectory','compare'):
        content.append(panel('Indicador em análise',dcc.Dropdown([{'label':v['name'],'value':k} for k,v in RULES['metrics'].items()],'cfo',id='metric',clearable=False,persistence=True,persistence_type='memory')))
        content.append(html.Div(id='metric-chart'))
        if key=='trajectory':content.append(panel('Comparação no período',comparison(rows,view)))
    elif key=='cash':
        content.append(panel('Do caixa operacional ao caixa residual',cash_chart(rows,colors),'LTM · US$ bilhões · FCL = FCO − CAPEX orgânico de caixa'))
        content.append(panel('Ponte por empresa',cash_table(rows),'Valores em US$ milhões · fluxos acumulados nos últimos 12 meses (LTM) · '+('reais aprovados' if dataset=='REAL' else 'dados demonstrativos')))
    elif key=='drivers':
        content.append(panel('KPI para comparar com os drivers',html.Div([
            dcc.Dropdown([{'label':'Sem sobreposição','value':'none'}]+[{'label':v['name'],'value':k} for k,v in RULES['metrics'].items()],
                         'none',id='driver-kpi',clearable=False,persistence=True,persistence_type='memory'),
            html.P('Driver no eixo esquerdo (linha contínua); KPI por empresa no eixo direito (linha tracejada). Fluxos e razões usam LTM; ROCE reportado segue a visão selecionada. A sobreposição não demonstra causalidade.',className='overlay-help'),
        ])))
        content.append(html.Div(id='driver-charts'))
        content.append(panel('Como ler os drivers',html.Div([
            html.P('Brent e câmbio são contexto comum: não mudam ao filtrar empresas. Mix de produção e margem de refino respondem à seleção de empresas; o trimestre limita o histórico e define o recorte do mix.'),
            html.P('Na base real, Brent usa contexto Yahoo BZ=F se disponível e câmbio usa PTAX Bacen coletada. Mix usa volumes trimestrais divulgados pelas empresas; Petrobras cobre Brasil. Perímetros e fatores de conversão diferem: consulte as ressalvas e fontes abaixo do gráfico. Margem de refino usa um benchmark comum EIA, sem representar a margem realizada de cada empresa. Leases, goodwill, aportes em JV e visão financeira não alteram o mix.' if dataset=='REAL' else 'Mix de gás é participação no volume de produção em boe, não na receita. As séries aqui são inteiramente sintéticas, sem correlação calculada com o desempenho financeiro. Leases, goodwill e visão financeira não alteram esses drivers.'),
            html.P('Fontes candidatas para a carga real (não são origem dos valores fictícios):') if dataset!='REAL' else None,
            html.Div([html.A('Bacen · PTAX ↗',href=RULES['fx']['source_url'],target='_blank',rel='noopener noreferrer'),html.A('Shell · databooks e contexto ↗',href='https://www.shell.com/investors/results-and-reporting/data-supplements.html',target='_blank',rel='noopener noreferrer'),html.A('TotalEnergies · resultados trimestrais ↗',href=data.SOURCES['TotalEnergies'],target='_blank',rel='noopener noreferrer')],className='driver-sources') if dataset!='REAL' else None,
        ])))
        content.append(panel('Capital de giro e impostos',html.P('Shell: trading e capital de giro. TotalEnergies: separar fluxo operacional estatutário das medidas ajustadas que excluem capital de giro. Esses fatores exigem reconciliação e não são ajustes automáticos.')))
    elif key=='quality' and dataset=='REAL':
        content.append(panel('Qualidade dos dados reais',table([{'empresa':r['company'],'KPI':k,'estado':v['status'],'motivo':v['reason']} for r in rows for k,v in r['quality'].items()])))
        from radar.ingestion.pipeline import batches
        content.append(panel('Publicações e responsáveis',table(batches().astype(str).to_dict('records'))))
    elif key=='quality':
        content.append(html.Div([panel('Estado da publicação',html.Div([badge('BLOQUEADO PARA USO FINANCEIRO','warning'),html.P('O dataset é sintético. Nenhum registro foi aprovado como resultado financeiro público.') ])),panel('Cobertura temporal',html.Div([badge('4 EMPRESAS · 8 TRIMESTRES'),html.P('LTM disponível apenas após quatro trimestres consecutivos. Valores indisponíveis não são substituídos por zero.')]))],className='two-col'))
        content.append(panel('Controles e evidências',table([{'controle':k,'estado':s,'evidência':e} for k,s,e in [('Completude temporal','APROVADO','8 períodos consecutivos no exemplo'),('Unicidade','APROVADO','Chave empresa + período + versão'),('Origem financeira pública','BLOQUEADO','Dataset demonstrativo'),('Reconciliação','REVISAO','Aguardando fatos e locators públicos'),('ROCE sintético','DEMONSTRAÇÃO','Fórmula implementada; alíquotas fictícias e capital empregado sintético'),('Original imutável','ATIVO','Upload preservado por SHA-256')]])))
    elif key=='method':
        content.append(html.Div([panel(v['name'],html.Div([badge(v['unit']),html.Div(v['formula'],className='formula'),html.P(v['note'].replace('Demonstração: alíquotas fictícias por empresa.','').strip() if dataset=='REAL' else v['note']),html.P(f"Regra v{RULES['version']} · "+('dados reais preservam evidências e revisão por lote.' if dataset=='REAL' else 'valores sintéticos não possuem evidência financeira pública.'))])) for v in RULES['metrics'].values()],className='two-col'))
        if dataset!='REAL':
            content.append(panel('Premissas do ROCE sintético',html.Div([html.P('EBIT ajustado = 65% do EBITDA sintético; itens especiais = zero. Imposto = EBIT × alíquota fictícia por empresa.'),table([{'empresa':c,'alíquota fictícia':f'{rate:.0%}'} for c,rate in RULES['synthetic_roce']['tax_rates'].items()]),html.P('Capital empregado sintético: PL + NCI + dívida financeira − caixa não operacional, goodwill incluído. Média dos saldos de abertura e fechamento da janela LTM. Leases excluídos na base e incluídos nos dois saldos na sensibilidade. Goodwill sintético = 10% do capital empregado em cada saldo; excluí-lo reduz apenas o denominador do ROCE. Nenhum resultado representa dados financeiros reais.') ])))
        content.append(panel('Catálogo de fontes oficiais',html.Div([html.A([html.Strong(c),html.Span(' Relações com investidores ↗')],href=url,target='_blank',rel='noopener noreferrer',className='source-link') for c,url in data.SOURCES.items()])))
        if dataset=='REAL':
            from radar.ingestion.production import production_dataset
            content.append(panel('Mix de produção · volumes trimestrais divulgados',html.Div([
                html.P(production_dataset()['method']),
                html.P('NÃO COMPARÁVEL: Petrobras cobre Brasil e gás total produzido; Chevron cobre produção líquida global incluindo consumo próprio; Shell cobre produção disponível para venda, incluindo afiliadas; TotalEnergies cobre participação econômica global. Shell converte gás a 5,8 mil pés cúbicos/boe; Chevron a 6; Total e Petrobras usam equivalências divulgadas. Condensados e LGN pertencem aos líquidos.'),
                html.P('A soma dos componentes deve conciliar com o total divulgado em até 2 mil boe/d, por arredondamento. Períodos ausentes permanecem indisponíveis. As fontes e localizações de cada trimestre estão nos detalhes do gráfico de mix.') ])))
            from radar.ingestion.refining import METHOD, LIMITATION
            content.append(panel('Margem indicativa de refino · benchmark comum',html.Div([
                html.P(METHOD),html.P(LIMITATION),
                html.P('Fonte: EIA, preços spot diários. Derivados em US$/galão americano multiplicados por 42; petróleo já em US$/barril. Não mistura Brent futuro Yahoo com preços spot. Datas sem algum dos três preços são excluídas, sem interpolação. Exige janela de coleta cobrindo o trimestre inteiro, pelo menos 40 datas comuns e cobertura de 90% das datas com qualquer uma das séries. Valores negativos são preservados.'),
                html.A('Definição de crack spread · EIA ↗',href='https://www.eia.gov/todayinenergy/includes/crackspread_explain.php',target='_blank',rel='noopener noreferrer') ])))
        content.append(panel('Câmbio · fonte aprovada',html.Div([html.P('Fonte oficial: Bacen · média trimestral da PTAX venda diária de fechamento para fluxos. BRL→USD por divisão pela cotação R$/USD; converter trimestre antes da soma LTM. Saldos: PTAX venda na data do balanço ou última publicação anterior.'),html.A('Consultar publicação oficial ↗',href=RULES['fx']['source_url'],target='_blank',rel='noopener noreferrer')])))
        content.append(panel('Imposto operacional · OPEN-03 aprovada',html.Div([html.P(RULES['operating_tax']['basis']),html.Ol([html.Li(step['description']) for step in RULES['operating_tax']['hierarchy']]),html.P('A pipeline exige imposto operacional divulgado ou reconstruído e conciliado com o EBIT.' if dataset=='REAL' else 'A pipeline exige imposto operacional divulgado ou reconstruído e conciliado com o EBIT. Alíquotas fictícias são usadas somente na base demonstrativa.') ])))
        content.append(panel('ROCE · alternativa com NOPAT divulgado',html.Div([html.P(RULES['operating_tax']['nopat_alternative']['method']),html.P(RULES['operating_tax']['nopat_alternative']['constraint'])])))
        content.append(panel('Alavancagem · alternativa aprovada para TotalEnergies',html.Div([html.P(RULES['ebitda_policy']['disclosed_alternative']['method']),html.P(RULES['ebitda_policy']['disclosed_alternative']['limitation'])])))
        content.append(panel('Shell · alternativas aprovadas, NÃO COMPARÁVEIS',html.Div([html.P(v) for k,v in RULES['shell_alternatives'].items() if k!='status'])))
        content.append(panel('Chevron · alternativas aprovadas, NÃO COMPARÁVEIS',html.Div([html.P(RULES['chevron_roce_alternative']['method']),html.P(RULES['chevron_roce_alternative']['limitation']),html.P(RULES['ebitda_policy']['chevron_approximation']['method']),html.P(RULES['ebitda_policy']['chevron_approximation']['limitation']),html.P(RULES['debt_policy']['retained_finance_leases']['method']),html.P(RULES['debt_policy']['retained_finance_leases']['limitation']),html.P(RULES['chevron_distribution_alternative']['method']),html.P(RULES['chevron_distribution_alternative']['limitation'])])))
        content.append(panel('Rastreabilidade',html.Div('Documento → localização → fato bruto → ajustes → normalização → cálculo → métrica → visual',className='formula')))
        content.append(panel('Goodwill e híbridos · política aprovada',html.Div([html.P(RULES['capital_policy']['goodwill_sensitivity']),html.P(RULES['capital_policy']['hybrids_base']),html.P(RULES['capital_policy']['hybrids_sensitivity'])])))
        content.append(panel('CAPEX e perímetro operacional · decisões aprovadas',html.Div([html.P(RULES['capex_policy']['base']),html.P(RULES['capex_policy']['jv_sensitivity']),html.P(RULES['capital_policy']['operating_perimeter']),html.P(RULES['capital_policy']['cash_nonoperating'])])))
        content.append(panel('Aprovação de dados · PoC',html.Div([html.P('Reconciliação: maior entre US$ 1 milhão, 0,1% do total de referência e arredondamento documentado. Variação superior a 30% gera alerta; base anterior zero exige revisão separada.'),html.P('Um responsável aprova mapeamentos, exceções e publicação. Valores não comparáveis preservam número e justificativa, com destaque visual, e aparecem nos gráficos com marcadores destacados e aviso na tooltip.') ])))
    elif key=='rules':
        content.append(panel('Regras financeiras versionadas',table([{'KPI':v['name'],'versão':RULES['version'],'fórmula':v['formula']} for v in RULES['metrics'].values()])))
        content.append(panel('Restatements',html.P('Lotes reais preservam mapeamento, regra, hash, conciliação e responsável. Novas publicações mantêm versões anteriores e nunca sobrescrevem os documentos.')))
    elif key=='admin':
        content.append(panel('Adicionar trimestre',html.Div([html.P('Cadastre um período no formato AAAAQn. O cadastro não gera fatos nem aprova resultados; os indicadores ficam indisponíveis até a carga.'),html.Div([dcc.Input(id='new-period',placeholder='Exemplo: 2026Q1',type='text',maxLength=6,className='text-input'),html.Button('Adicionar trimestre',id='add-period',n_clicks=0,className='button')],className='period-form'),html.Div(id='period-result',role='status')])))
        content.append(panel('Preservar documento original',html.Div([html.P('PDF, XLSX, CSV ou HTML · até 20 MB. O upload preserva o original e registra sua origem para revisão. Não publica valores automaticamente.'),html.Div([dcc.Dropdown(list(data.COMPANIES),'Petrobras',id='upload-company',clearable=False),dcc.Dropdown(data.periods(),period,id='upload-period',clearable=False)],className='two-col'),dcc.Input(id='source-url',placeholder='URL pública original (https://...)',type='url',className='text-input'),dcc.Input(id='locator',placeholder='Localização: página, tabela, linha ou célula',className='text-input'),html.Div([html.Div(['↑',html.H3(['Selecione ou arraste um documento ',html.Small('(bloqueado pela SI Petrobras)',className='upload-blocked-note')]),html.P('O original será preservado com hash SHA-256')],className='upload-zone upload-disabled',title='A Segurança da Informação da Petrobras bloqueia automaticamente sites que ofereçam funcionalidade de upload de arquivos.',**{'aria-disabled':'true'}),dcc.Store(id='upload-file'),dcc.Store(id='upload-filename')]),html.Div(id='upload-result',role='status') ])))
        docs=data.documents(); content.append(panel('Histórico de documentos',document_table(docs.astype(str).to_dict('records'))))
        from radar.web.ingestion import controls
        content.extend(controls(panel,table))
    return [title,'Compare empresas, acompanhe o ciclo e entenda o que sustenta a geração de valor.',content]+['nav-link active' if k==key else 'nav-link' for k,_,_ in NAV]

def fmt(value,suffix=''):
    return 'Indisponível' if value is None else f'{value:,.1f}'.replace(',','X').replace('.',',').replace('X','.')+suffix

def metric_quality(row, metric, view='standard'):
    key = 'reported_quality' if metric == 'roce' and view == 'reported' else 'quality'
    return row.get(key, {}).get(metric, {})


def comparability_notice(title, content, class_name='non-comparable'):
    return html.Details([html.Summary([html.Strong(title),html.Span(' — ver detalhes',className='notice-expand-hint')]),content],
                        className=class_name+' collapsible-notice',open=False)


def breakeven_panel(period, rows, sensitivities=None, metric='none', view='standard'):
    from radar.ingestion.breakeven import cash_breakeven, METHOD, LIMITATION
    results=cash_breakeven(period,rows)
    fig=go.Figure()
    for key,label,pattern in [('organic','Orgânico',''),('after_distribution','Após distribuições','/')]:
        fig.add_bar(name=label,x=[r['company'] for r in results],y=[r[key] for r in results],
                    marker_color=[data.COMPANIES[r['company']][0] for r in results],
                    marker_pattern=dict(shape=pattern,size=12,solidity=.06),
                    hovertemplate='%{x}<br>%{y:.2f} US$/barril<extra>'+label+'</extra>')
    fig.update_layout(barmode='group');fig.update_yaxes(title_text='US$/barril')
    records=[{'empresa':r['company'],'orgânico (US$/b)':fmt(r['organic']),
              'após distribuições (US$/b)':fmt(r['after_distribution']),
              'Brent spot LTM (US$/b)':fmt(r['brent']),'líquidos LTM (milhões bbl)':fmt(r['volume'])} for r in results]
    details=html.Div([html.P(METHOD),html.P(LIMITATION),value_table(records),
        html.Ul([html.Li([html.Strong(r['company']+': '),justification(r['reason'])]) for r in results]),
        html.P('Volumes: média diária × dias de cada trimestre; quatro trimestres consecutivos. Brent: média dos preços spot diários disponíveis, com pelo menos 40 observações por trimestre. Sem interpolação.'),
        html.A('Brent spot · EIA ↗',href='https://www.eia.gov/dnav/pet/hist/RBRTED.htm',target='_blank',rel='noopener noreferrer'),
        html.Ul([html.Li([r['company']+' · '+source['period']+': ',html.A('Fonte de produção ↗',href=source['source_url'],target='_blank',rel='noopener noreferrer')]) for r in results for source in r['sources']])])
    history=[]
    companies=[r['company'] for r in rows]
    for p in data.periods():
        if p<=period:
            history.extend(dict(r,period=p) for r in cash_breakeven(p,data.metrics(p,companies,dataset='REAL',include_jv='include_jv' in (sensitivities or []))))
    charts=[]
    for key,label in [('organic','Equilíbrio orgânico'),('after_distribution','Equilíbrio após distribuições')]:
        historical=go.Figure()
        available=sorted({r['period'] for r in history if r[key] is not None})
        for company in companies:
            points=[r for r in history if r['company']==company and r['period'] in available]
            historical.add_scatter(x=[r['period'] for r in points],y=[r[key] for r in points],
                name=company,mode='lines+markers',connectgaps=False,
                line=dict(color=data.COMPANIES[company][0],width=3),
                marker=dict(symbol='diamond-open',size=9),
                hovertemplate='%{x}<br>%{y:.2f} US$/barril<extra>%{fullData.name}</extra>')
        historical.update_xaxes(type='category',categoryorder='array',categoryarray=available,
                                tickmode='array',tickvals=available)
        historical.update_yaxes(title_text='US$/barril')
        if metric and metric!='none':
            for company in companies:
                values=[];flags=[]
                for p in available:
                    row=data.metrics(p,[company],leases='include_leases' in (sensitivities or []),
                        exclude_goodwill='exclude_goodwill' in (sensitivities or []),
                        dataset='REAL',include_jv='include_jv' in (sensitivities or []))[0]
                    values.append(row['reported_roce'] if metric=='roce' and view=='reported' else row[metric])
                    flags.append(metric_quality(row,metric,view).get('status')=='NAO_COMPARAVEL')
                historical.add_scatter(x=available,y=values,name=company+' · '+RULES['metrics'][metric]['name'],
                    yaxis='y2',mode='lines+markers',connectgaps=False,
                    line=dict(color=data.COMPANIES[company][0],dash='dash',width=2),
                    marker=dict(symbol=['diamond-open' if f else 'diamond' for f in flags],
                                size=[11 if f else 6 for f in flags],line=dict(width=2)),
                    hovertemplate='%{x}<br>%{y:.2f} '+RULES['metrics'][metric]['unit']+'<extra>%{fullData.name}</extra>')
            historical.update_layout(yaxis2=dict(title=RULES['metrics'][metric]['name']+' · '+RULES['metrics'][metric]['unit'],
                overlaying='y',side='right',showgrid=False,automargin=True,nticks=6,zeroline=False),
                margin=dict(l=75,r=90,t=30,b=110),legend=dict(orientation='h',y=-.2,x=0,font=dict(size=11)))
        if not available:
            historical.add_annotation(text='Sem dados completos para o período selecionado.',showarrow=False,xref='paper',yref='paper',x=.5,y=.5)
        chart=graph(historical,height=520)
        chart.figure.update_layout(margin=dict(l=75,r=90,t=25,b=150),
            legend=dict(orientation='h',x=0,y=-.25,yanchor='top',font=dict(size=11)))
        charts.append(panel(label,chart,'Estimativa LTM · quatro trimestres consecutivos · até '+period))
    return html.Div([panel('Brent de equilíbrio de caixa — estimado',html.Div([graph(fig),methodology_sources(details)]),period+' · LTM · cenário com sensibilidade de US$ 1 por barril de líquidos · demais fatores constantes'),*charts])


def methodology_sources(content):
    return html.Details([html.Summary('Metodologia e Fontes'),content],
                        className='methodology-sources collapsible-notice',open=False)


def justification(reason):
    """Keep the methodological explanation, without repeating status labels."""
    cleaned=re.sub(r'\bN[ÃA]O[\s-]+COMPAR[ÁA]VEL\b[.:]?', '',reason or '',flags=re.I)
    return '; '.join(dict.fromkeys(part.strip(' .;,') for part in cleaned.split(';') if part.strip(' .;,')))


def warning_icon(reason):
    text=justification(reason)
    return html.Span('⚠',className='metric-warning-icon',title=text,tabIndex=0,role='img',**{'aria-label':text})


def value_table(records, labels=None):
    if not records:return html.P('Nenhum registro disponível.',className='empty')
    keys=list(records[0])
    return html.Div(html.Table([
        html.Thead(html.Tr([html.Th((labels or {}).get(k,k.capitalize()),scope='col') for k in keys])),
        html.Tbody([html.Tr([html.Td(row[k]) for k in keys]) for row in records])
    ],className='value-table'),className='value-table-container')


def document_table(records):
    for record in records:
        # Markdown is enabled only for filenames; escape filenames from uploaded documents.
        label=''.join('\\'+c if c in '\\`*_{}[]()#+.!|>~-' else c for c in record['filename'])
        record['filename']='['+label+'](/original/'+record['hash']+')'
    result=table(records,column_labels={'filename':'Documento'})
    if records:
        result.columns=[dict(column,presentation='markdown') if column['id']=='filename' else column for column in result.columns]
        result.markdown_options={'link_target':'_blank','html':False}
    return result


def metric_cell(row, metric, view):
    quality = metric_quality(row, metric, view)
    value = row['reported_roce'] if metric == 'roce' and view == 'reported' else row[metric]
    suffix = {'roce':'%','cfo':' mi','leverage':'x','capex':'%','distribution':'%'}[metric]
    return html.Div([
        html.Span(RULES['metrics'][metric]['name']),
        html.Strong([fmt(value,suffix),warning_icon(quality.get('reason','')) if quality.get('status')=='NAO_COMPARAVEL' else None]),
    ],className='metric-row',
       title=None if quality.get('status')=='NAO_COMPARAVEL' else RULES['metrics'][metric]['formula']+' · '+RULES['metrics'][metric]['note'].replace('Demonstração: alíquotas fictícias por empresa.','').strip())


def comparison(rows,view):
    return html.Div([html.Div([
        html.Div([html.Span(r['company'][0],className='company-monogram',
                  style={'backgroundColor':data.COMPANIES[r['company']][0]}),
                  html.Div([html.H4(r['company']),html.Small(data.COMPANIES[r['company']][1])])],className='company-heading'),
        *[metric_cell(r,k,view) for k in RULES['metrics']],
        html.A('Definições e fontes ↗',href='/method',className='company-source')
    ],className='company-card') for r in rows],className='company-grid')


def cash_table(rows):
    records = []
    dependencies = {'FCO':['cfo'], 'CAPEX':['cfo','capex'], 'FCL':['cfo','capex'],
                    'distribuições':['cfo','distribution'], 'caixa residual':['cfo','capex','distribution']}
    for row in rows:
        record = {'empresa':row['company'],'FCO':fmt(row['cfo']),
                  'CAPEX':fmt((row['cfo'] or 0)*(row['capex'] or 0)/100),
                  'FCL':fmt(row['fcf']),
                  'distribuições':fmt((row['cfo'] or 0)*(row['distribution'] or 0)/100),
                  'caixa residual':fmt(row['residual'])}
        for key, metrics in dependencies.items():
            reasons = [metric_quality(row,m)['reason'] for m in metrics
                       if metric_quality(row,m).get('status') == 'NAO_COMPARAVEL']
            if reasons:
                reason='; '.join(dict.fromkeys(reasons))
                record[key] = html.Span([record[key],warning_icon(reason)],className='numeric-value')
        records.append(record)
    return value_table(records,{'FCO':'FCO','CAPEX':'CAPEX','FCL':'FCL'})

def period_comparison(metric, rows, view, period_label):
    """Compare one common reference period without a historical trajectory."""
    name=RULES['metrics'][metric]['name'];unit=RULES['metrics'][metric]['unit']
    fig=go.Figure();records=[]
    for row in rows:
        quality=metric_quality(row,metric,view)
        value=row['reported_roce'] if metric=='roce' and view=='reported' else row[metric]
        flagged=quality.get('status')=='NAO_COMPARAVEL'
        fig.add_bar(x=[row['company']],y=[value],name=row['company'],showlegend=False,
                    marker_color=data.COMPANIES[row['company']][0],marker_pattern=dict(shape='/' if flagged else '',size=12,solidity=.06,fgcolor='rgba(255,255,255,0.3)'),
                    hovertemplate='%{x}<br>%{y:.2f} '+unit+'<extra></extra>')
        records.append({'empresa':row['company'],'valor':html.Span([fmt(value),warning_icon(quality.get('reason','')) if flagged else None],className='numeric-value'),'unidade':unit})
    fig.update_yaxes(title_text=unit)
    return html.Div([panel(name+' · '+period_label,graph(fig),'Comparação entre empresas na mesma referência'),
                     panel('Valores por empresa',value_table(records))])


def cash_chart(rows,colors):
    fig=go.Figure()
    for label,key,color in [('FCO','cfo','#008542'),('FCL','fcf','#00a397'),('Caixa residual','residual','#b9c9bd')]:
        flags=[]
        for row in rows:
            qualities=[metric_quality(row,m) for m in {'cfo':['cfo'],'fcf':['cfo','capex'],'residual':['cfo','capex','distribution']}[key]]
            reasons=[q['reason'] for q in qualities if q.get('status')=='NAO_COMPARAVEL']
            flags.append(bool(reasons))
        fig.add_bar(name=label,x=[r['company'] for r in rows],y=[r[key]/1000 if r[key] is not None else None for r in rows],
                    marker_color=color,marker_pattern=dict(shape=['/' if f else '' for f in flags],size=12,solidity=.06,fgcolor='rgba(255,255,255,0.3)'),marker_cornerradius=4,
                    hovertemplate='%{x}<br>%{y:.2f} US$ bi<extra>'+label+'</extra>')
    fig.update_layout(barmode='group',bargap=.35); return graph(fig)

@app.callback(Output('metric-chart','children'),Input('metric','value'),Input('companies','value'),Input('period','value'),Input('view','value'),Input('sensitivities','value'),Input('dataset','value'),Input('location','pathname'))
def metric_chart(metric,companies,period,view,sensitivities,dataset="DEMONSTRACAO",pathname="/trajectory"):
    if pathname=="/compare":
        rows=data.metrics(period,companies or [],'include_leases' in (sensitivities or []),exclude_goodwill='exclude_goodwill' in (sensitivities or []),dataset=dataset,include_jv='include_jv' in (sensitivities or []))
        return period_comparison(metric,rows,view,period+" · LTM")
    fig=go.Figure()
    for company in companies or []:
        vals=[]; flags=[]; periods=[p for p in data.periods() if p<=period]
        for p in periods:
            row=data.metrics(p,[company],'include_leases' in (sensitivities or []),exclude_goodwill='exclude_goodwill' in (sensitivities or []),dataset=dataset,include_jv='include_jv' in (sensitivities or []))[0]
            quality=metric_quality(row,metric,view)
            value=row['reported_roce'] if metric=='roce' and view=='reported' else row[metric]
            vals.append(value)
            flagged=quality.get('status')=='NAO_COMPARAVEL'
            flags.append(flagged)
        fig.add_scatter(x=periods,y=vals,name=company,mode='lines+markers',connectgaps=False,line=dict(color=data.COMPANIES[company][0],width=3),marker=dict(size=[11 if f else 7 for f in flags],symbol=['diamond-open' if f else 'circle' for f in flags],line=dict(width=2)),hovertemplate='%{x}<br>%{y:.2f} '+RULES['metrics'][metric]['unit']+'<extra>%{fullData.name}</extra>')
    available_periods=sorted({p for trace in fig.data for p,value in zip(trace.x,trace.y) if value is not None})
    for trace in fig.data:
        keep=[i for i,p in enumerate(trace.x) if p in available_periods]
        trace.x=[trace.x[i] for i in keep]
        trace.y=[trace.y[i] for i in keep]
        trace.marker.size=[trace.marker.size[i] for i in keep]
        trace.marker.symbol=[trace.marker.symbol[i] for i in keep]
    fig.update_xaxes(type='category',categoryorder='array',categoryarray=available_periods,
                     tickmode='array',tickvals=available_periods)
    return panel(RULES['metrics'][metric]['name'],html.Div([graph(fig)]),RULES['metrics'][metric]['formula']+' · '+RULES['metrics'][metric]['unit'])

@app.callback(Output('driver-charts','children'),Input('driver-kpi','value'),Input('companies','value'),Input('period','value'),Input('view','value'),Input('sensitivities','value'),Input('dataset','value'))
def driver_charts(metric,companies,period,view,sensitivities,dataset="DEMONSTRACAO"):
    companies=companies or []
    from radar.web.drivers import financial_periods
    periods=financial_periods(period,companies,dataset)
    figures=(real_figures if dataset=="REAL" else driver_figures)(period,companies,{c:v[0] for c,v in data.COMPANIES.items()},allowed_periods=periods)
    if metric and metric != 'none':
        for company in companies:
            values=[]; flags=[]
            for p in periods:
                row=data.metrics(p,[company],'include_leases' in (sensitivities or []),
                                 exclude_goodwill='exclude_goodwill' in (sensitivities or []),dataset=dataset,include_jv='include_jv' in (sensitivities or []))[0]
                quality=metric_quality(row,metric,view)
                value=row['reported_roce'] if metric=='roce' and view=='reported' else row[metric]
                flagged=quality.get('status')=='NAO_COMPARAVEL'
                flags.append(flagged)
                values.append(value)
            for key in ('brent','fx','margin'):
                figures[key].add_scatter(x=periods,y=values,name=company+' · '+RULES['metrics'][metric]['name'],
                    yaxis='y2',mode='lines+markers',connectgaps=False,
                    line=dict(color=data.COMPANIES[company][0],dash='dash',width=2),marker=dict(symbol=['diamond-open' if f else 'diamond' for f in flags],size=[11 if f else 6 for f in flags],line=dict(width=2)),
                    hovertemplate='%{x}<br>%{y:.2f} '+RULES['metrics'][metric]['unit']+'<extra>%{fullData.name}</extra>')
                figures[key].update_layout(yaxis2=dict(title=RULES['metrics'][metric]['name']+' · '+RULES['metrics'][metric]['unit'],
                    overlaying='y',side='right',showgrid=False,automargin=True,nticks=6,zeroline=False))
    cards=[]
    for key,title,subtitle in [
        ('brent','Brent · cenário demonstrativo','US$/barril · média trimestral fictícia'),
        ('fx','Câmbio BRL/USD · cenário demonstrativo','R$/US$ · média trimestral fictícia; PTAX Bacen ainda não carregada'),
        ('gas','Mix de produção · gás e líquidos','% da produção em boe · '+period+' · dados fictícios'),
        ('margin','Margem de refino · cenário demonstrativo','US$/barril · margem unitária fictícia em base comum')]:
        if dataset=='REAL':
            title={'brent':'Brent futuro · Yahoo Finance','fx':'Câmbio · PTAX Bacen','gas':'Mix de produção · gás e líquidos','margin':'Margem indicativa de refino · benchmark comum'}[key]
            subtitle={'brent':'US$/barril · média dos fechamentos diários disponíveis de BZ=F; não equivale ao Brent físico','fx':'R$/US$ · média trimestral da PTAX venda diária de fechamento','gas':'% dos volumes médios diários em boe · '+period+' · Petrobras: Brasil; demais: global · líquidos na cor da empresa, gás em cinza','margin':'US$/barril · Brent spot e derivados do Golfo dos EUA · média trimestral 3–2–1 · mesmo benchmark para todos os peers'}[key]
        chart=graph(figures[key],height=560 if metric!='none' and key!='gas' else 460)
        chart.figure.update_layout(margin=dict(l=75,r=90,t=30,b=110),
                                   legend=dict(orientation='h',y=-.2,x=0,font=dict(size=11)))
        if key!='gas':
                chart.figure.update_xaxes(type='category',tickmode='array',tickvals=periods,
                                     ticktext=[p[:4]+' T'+p[-1] for p in periods],tickangle=0,automargin=True)
        if dataset=='REAL' and key=='gas':
            from radar.ingestion.production import production_mix, production_dataset
            mix=production_mix(period,companies,periods)
            details=html.Div([
                html.P(production_dataset()['method']),
                table([{'empresa':r['company'],'perímetro':r['scope'],'líquidos (mil b/d)':fmt(r['liquids_kbd']),
                        'gás (mil boe/d)':fmt(r['gas_kboed']),'gás (%)':fmt(r['gas_share_pct']),
                        'diferença de conciliação (mil boe/d)':fmt(r['reconciliation_delta_kboed'])} for r in mix]),
                html.Ul([html.Li([html.Strong(r['company']+' · '+r['period']+': '),r['note'],' ',
                                  html.A('Fonte original ↗',href=r['source_url'],target='_blank',rel='noopener noreferrer'),
                                  html.Small(' · '+r['locator'])]) for r in mix]),
                html.P('A soma de gás e líquidos é conciliada com o total divulgado; tolerância de 2 mil boe/d para arredondamento dos componentes. Não há interpolação ou substituição por trimestre anterior.')])
            chart=html.Div([chart,methodology_sources(details) if mix else None])
        if dataset=='REAL' and key=='margin':
            from radar.ingestion.refining import refining_snapshot,quarterly_margins
            snapshot=refining_snapshot()
            coverage=quarterly_margins(snapshot,periods)
            chart=html.Div([chart,methodology_sources(html.Div([
                html.P(snapshot['method']),html.P(snapshot['limitation']),
                table([{'trimestre':r['period'],'margem (US$/barril)':fmt(r['value']),
                        'datas comuns':r['observations'],'datas excluídas':r['excluded_dates'],
                        'cobertura (%)':fmt(r['coverage_pct'])} for r in coverage]),
                html.P('Datas excluídas não possuem todos os preços. Sem interpolação; mínimo de 40 datas comuns, 90% de cobertura e intervalo de coleta abrangendo o trimestre inteiro. Valores negativos são mantidos.'),
                html.Ul([html.Li(html.A(v['title']+' · '+v['unit']+' ↗',href=v['url'],target='_blank',rel='noopener noreferrer')) for v in snapshot['series'].values()])]))])
        cards.append(panel(title,chart,subtitle))
    result=[html.Div(cards,className='driver-grid')]
    if dataset=='REAL':
        rows=data.metrics(period,companies,dataset='REAL',include_jv='include_jv' in (sensitivities or []))
        result.append(breakeven_panel(period,rows,sensitivities,metric,view))
    return result

@app.callback(Output('period','options'),Input('location','pathname'),Input('period-revision','data'))
def refresh_period_options(path,revision):
    return data.periods()


@app.callback(Output('period-result','children'),Output('period-revision','data'),Output('upload-period','options'),
              Input('add-period','n_clicks'),State('new-period','value'),prevent_initial_call=True)
def register_period(clicks,period):
    if not clicks: return no_update,no_update,no_update
    period=(period or '').strip().upper()
    try:
        added=data.add_period(period)
    except ValueError as error:
        return html.P(str(error),className='error'),no_update,no_update
    message=f'{period} cadastrado. Disponível nos filtros e no upload; dados ainda não carregados.' if added else f'{period} já está cadastrado.'
    return html.P(message),{'period':period,'revision':clicks},data.periods()


@app.callback(Output('upload-result','children'),Input('upload-file','data'),State('upload-filename','data'),State('upload-company','value'),State('upload-period','value'),State('source-url','value'),State('locator','value'),prevent_initial_call=True)
def upload(contents,filename,company,period,url,locator):
    if not contents: return no_update
    if not url or not url.startswith('https://') or not locator: return html.P('Informe a URL pública HTTPS e a localização no documento.',className='error')
    if Path(filename).suffix.lower() not in ('.pdf','.xlsx','.csv','.html'): return html.P('Tipo de arquivo não permitido.',className='error')
    try:
        content=base64.b64decode(contents.split(',',1)[1],validate=True)
        if len(content)>20*1024*1024: return html.P('Arquivo excede 20 MB.',className='error')
        if filename.lower().endswith('.pdf') and not content.startswith(b'%PDF'): return html.P('Conteúdo PDF inválido.',className='error')
        if filename.lower().endswith('.xlsx') and not content.startswith(b'PK'): return html.P('Conteúdo XLSX inválido.',className='error')
        digest,status=data.preserve(content,filename,company,period,url,locator)
        return html.Div([badge(status),html.P('Original preservado. Aguarda extração, reconciliação e aprovação.'),html.Code(digest),html.Br(),html.A('Baixar original',href='/original/'+digest)])
    except (ValueError,TypeError): return html.P('Não foi possível validar o arquivo.',className='error')

@app.callback(Output('dataset-badge','children'),Output('dataset-notice','children'),Output('export-link','href'),Input('dataset','value'))
def dataset_labels(dataset):
    real=dataset=='REAL'
    return badge('REAIS APROVADOS' if real else 'BASE DEMONSTRATIVA','warning'),('Dados reais aprovados. Cobertura parcial: componentes ausentes permanecem indisponíveis.' if real else 'Dados sintéticos para explorar o produto. Não representam resultados financeiros reais.'),'/export?dataset='+dataset

from radar.web.ingestion import callbacks as ingestion_callbacks
ingestion_callbacks(app,panel,table,badge)

if __name__=='__main__': app.run(host='127.0.0.1',port=int(os.environ.get('PORT','8050')),debug=False)
