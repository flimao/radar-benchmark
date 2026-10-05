import base64, io, json, os, secrets, time
from pathlib import Path
from collections import defaultdict
from flask import Flask, session, request, redirect, Response, send_file, abort
from werkzeug.security import check_password_hash
from dash import Dash, html, dcc, Input, Output, State, dash_table, no_update
import plotly.graph_objects as go
from radar import data
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
    frame=data.export(); return Response(frame.to_csv(index=False),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=radar-demonstracao.csv'})

@server.route('/original/<digest>')
def original(digest):
    if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest): abort(404)
    path=data.ROOT/'data/original'/digest
    if not path.exists(): abort(404)
    return send_file(path,as_attachment=True,download_name=digest)

app=Dash(__name__,server=server,title='RADAR · Benchmarking de energia',assets_folder=str(Path(__file__).parent/'assets'),suppress_callback_exceptions=True)
NAV=[('overview','◫','Resumo executivo'),('trajectory','↗','Posição e trajetória'),('compare','≋','Comparação por KPI'),('drivers','◎','Drivers e contexto'),('cash','⇄','Ponte de caixa'),('quality','◇','Qualidade dos dados'),('method','▤','Metodologia e fontes'),('rules','⤺','Regras e revisões'),('upload','⊕','Administração de carga')]
def badge(text,kind=''): return html.Span(text,className='badge '+kind)
def panel(title,children,subtitle=None): return html.Section([html.Div([html.H3(title),html.P(subtitle) if subtitle else None],className='panel-head'),children],className='panel')
def graph(fig):
    fig.update_layout(template='plotly_white',font=dict(family='system-ui',color='#53615b',size=12),margin=dict(l=45,r=24,t=20,b=38),paper_bgcolor='white',plot_bgcolor='white',legend=dict(orientation='h',y=1.12,x=0),height=300)
    fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor='#edf1ee',zerolinecolor='#edf1ee')
    return dcc.Graph(figure=fig,config={'displayModeBar':False,'responsive':True})
def table(rows, column_labels=None, flagged_cells=None):
    if not rows: return html.P('Nenhum registro disponível.',className='empty')
    return dash_table.DataTable(data=rows,columns=[{'name':(column_labels or {}).get(k,k.replace('_',' ').capitalize()),'id':k} for k in rows[0]],style_table={'overflowX':'auto'},style_cell={'fontFamily':'system-ui','textAlign':'left','padding':'16px','fontSize':13,'border':'none','color':'#344b40'},style_header={'backgroundColor':'#f5f8f6','fontWeight':600,'border':'none'},style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'#fafcfb'}]+[{'if':{'row_index':index,'column_id':key},'backgroundColor':'#fff0e8','color':'#852800','fontWeight':'bold','border':'2px solid #a33b0a','whiteSpace':'normal'} for index,key in (flagged_cells or [])],page_size=12)
app.layout=html.Div([
    dcc.Location(id='location'),
    html.A('Ir para o conteúdo',href='#content',className='skip'),
    html.Aside([html.A([html.Span('◉',className='brand-icon'),'RADAR',html.Span('ENERGY INTELLIGENCE',className='brand-caption')],href='/',className='brand'),html.Div('WORKSPACE',className='nav-label'),html.Nav([html.A([html.Span(icon,className='nav-icon'),label],href='/' if key=='overview' else '/'+key,id='nav-'+key,className='nav-link') for key,icon,label in NAV]),html.Div([html.Div('RESILIÊNCIA QUE GERA VALOR',className='sidebar-note'),html.P('Uma visão comparável.\nDecisões com contexto.'),html.Div([html.Span('●',className='green-dot'),' Ambiente de demonstração'],className='environment')],className='sidebar-footer')],className='sidebar'),
    html.Div([html.Header([html.Div([html.Span('Benchmarking financeiro',className='breadcrumb'),html.Span(' / '),html.Span('Óleo e gás')]),html.Div([badge('BASE DEMONSTRATIVA','warning'),html.Span('PT-BR',className='locale'),html.Div('RA',className='avatar')],className='header-actions')],className='topbar'),
    html.Main([html.Div([html.Div([html.Div('INTELIGÊNCIA PARA DECISÃO',className='eyebrow'),html.H1(id='page-title'),html.P(id='page-description',className='page-description')]),html.A(['↓  Exportar dados'],href='/export',className='button secondary')],className='page-heading'),
    html.Div([html.Div([html.Label('EMPRESAS'),dcc.Dropdown(list(data.COMPANIES),list(data.COMPANIES),multi=True,id='companies',clearable=False)],className='filter companies'),html.Div([html.Label('TRIMESTRE DE REFERÊNCIA'),dcc.Dropdown(data.PERIODS,'2025Q4',id='period',clearable=False)],className='filter'),html.Div([html.Label('VISÃO DOS INDICADORES'),dcc.Dropdown([{'label':'Padronizado · LTM','value':'standard'},{'label':'Reportado · ROCE','value':'reported'}],'standard',id='view',clearable=False)],className='filter'),html.Div([html.Label('SENSIBILIDADES'),dcc.Dropdown([{'label':'Incluir leases','value':'include_leases'},{'label':'Excluir goodwill','value':'exclude_goodwill'}],[],id='sensitivities',multi=True,clearable=True,placeholder='Base: sem leases, com goodwill'),html.Small('Nenhuma seleção = sem leases, com goodwill',className='sensitivity-hint')],className='filter')],className='filters'),
    html.Div([html.Span('ⓘ'),html.Span('Dados sintéticos para explorar o produto. Não representam resultados financeiros reais. Fontes oficiais estão disponíveis no catálogo.')],className='demo-notice'),html.Div(id='page-content'),html.Footer([html.Span('RADAR  /  Resiliência que gera valor'),html.Span(f"USD · regras v{RULES['version']} · nenhuma recomendação de investimento")])],id='content')],className='workspace')],className='shell')

@app.callback(Output('page-title','children'),Output('page-description','children'),Output('page-content','children'),*[Output('nav-'+key,'className') for key,_,_ in NAV],Input('location','pathname'),Input('companies','value'),Input('period','value'),Input('view','value'),Input('sensitivities','value'))
def render(path,companies,period,view,sensitivities):
    key=(path or '/').strip('/') or 'overview'; key=key if key in [n[0] for n in NAV] else 'overview'
    title=next(n[2] for n in NAV if n[0]==key); rows=data.metrics(period,companies or [],'include_leases' in (sensitivities or []),exclude_goodwill='exclude_goodwill' in (sensitivities or [])); df=data.facts(); colors={c:v[0] for c,v in data.COMPANIES.items()}
    content=[]
    if key=='overview':
        descriptions=[('4','Empresas no radar','IFRS e US GAAP'),('8','Trimestres disponíveis','Histórico demonstrativo'),('5','Indicadores essenciais','Retorno, caixa e disciplina'),('LTM','Perspectiva de análise','Quatro trimestres completos')]
        content.append(html.Div([html.Div([html.Div(label,className='stat-label'),html.Div(value,className='stat-value'),html.Div(note,className='stat-note')],className='stat') for value,label,note in descriptions],className='stats'))
        content.append(html.Div([html.Div([badge('PANORAMA DO SETOR'),html.H2(['Resiliência que',html.Br(),'gera valor.']),html.P('Observe a capacidade de gerar caixa, sustentar investimentos e remunerar acionistas ao longo do ciclo.'),html.A('Explorar a trajetória  ↗',href='/trajectory',className='hero-link')],className='hero'),panel('Geração e alocação de caixa',cash_chart(rows,colors),'Fluxos LTM · US$ bilhões · dados demonstrativos')],className='overview-grid'))
        content.append(panel('As empresas, lado a lado',comparison(rows,view),'Perspectivas complementares, sem ranking composto. Clique em uma empresa para consultar as definições.'))
        content.append(html.Div([panel('Uma leitura em cinco etapas',html.Div([html.Span(x) for x in ['01  Posição','02  Trajetória','03  Resiliência','04  Geração de valor','05  Decisão']],className='journey')),panel('Transparência em cada indicador',html.Div([badge('DEMONSTRAÇÃO','warning'),html.P('ROCE calculado com componentes sintéticos e alíquotas fictícias: Chevron 10%, Shell 20%, Petrobras e Equinor 25%. Os valores reportados do exemplo são sintéticos.'),html.A('Consultar metodologia  →',href='/method')]))],className='two-col'))
    elif key in ('trajectory','compare'):
        content.append(panel('Indicador em análise',dcc.Dropdown([{'label':v['name'],'value':k} for k,v in RULES['metrics'].items()],'cfo',id='metric',clearable=False,persistence=True,persistence_type='memory')))
        content.append(html.Div(id='metric-chart'))
        content.append(panel('Comparação no período',comparison(rows,view)))
    elif key=='cash':
        content.append(panel('Do caixa operacional ao caixa residual',cash_chart(rows,colors),'LTM · US$ bilhões · FCL = FCO − CAPEX orgânico de caixa'))
        content.append(panel('Ponte por empresa',cash_table(rows),'Valores em US$ milhões · fluxos acumulados nos últimos 12 meses (LTM) · dados demonstrativos'))
    elif key=='drivers':
        content.append(html.Div([panel('Ciclo e preço do petróleo',html.P('Brent, preços realizados e margens de refino afetam o caixa. Séries públicas de contexto ainda não foram carregadas.')),panel('Capital de giro e impostos',html.P('Shell: trading e capital de giro. Equinor: calendário fiscal. Esses fatores exigem reconciliação e não são ajustes automáticos.')),panel('Investimento e perímetro',html.P('Separar CAPEX orgânico, M&A e alienações. Mudanças de perímetro devem criar flags e versões.')),panel('Normas contábeis',table([{'empresa':c,'norma':data.COMPANIES[c][1],'país':data.COMPANIES[c][2]} for c in companies or []]))],className='two-col'))
    elif key=='quality':
        content.append(html.Div([panel('Estado da publicação',html.Div([badge('BLOQUEADO PARA USO FINANCEIRO','warning'),html.P('O dataset é sintético. Nenhum registro foi aprovado como resultado financeiro público.') ])),panel('Cobertura temporal',html.Div([badge('4 EMPRESAS · 8 TRIMESTRES'),html.P('LTM disponível apenas após quatro trimestres consecutivos. Valores indisponíveis não são substituídos por zero.')]))],className='two-col'))
        content.append(panel('Controles e evidências',table([{'controle':k,'estado':s,'evidência':e} for k,s,e in [('Completude temporal','APROVADO','8 períodos consecutivos no exemplo'),('Unicidade','APROVADO','Chave empresa + período + versão'),('Origem financeira pública','BLOQUEADO','Dataset demonstrativo'),('Reconciliação','REVISAO','Aguardando fatos e locators públicos'),('ROCE sintético','DEMONSTRAÇÃO','Fórmula implementada; alíquotas fictícias e capital empregado sintético'),('Original imutável','ATIVO','Upload preservado por SHA-256')]])))
    elif key=='method':
        content.append(html.Div([panel(v['name'],html.Div([badge(v['unit']),html.Div(v['formula'],className='formula'),html.P(v['note']),html.P(f"Regra v{RULES['version']} · valores sintéticos não possuem evidência financeira pública.")])) for v in RULES['metrics'].values()],className='two-col'))
        content.append(panel('Premissas do ROCE sintético',html.Div([html.P('EBIT ajustado = 65% do EBITDA sintético; itens especiais = zero. Imposto = EBIT × alíquota fictícia por empresa.'),table([{'empresa':c,'alíquota fictícia':f'{rate:.0%}'} for c,rate in RULES['synthetic_roce']['tax_rates'].items()]),html.P('Capital empregado sintético: PL + NCI + dívida financeira − caixa não operacional, goodwill incluído. Média dos saldos de abertura e fechamento da janela LTM. Leases excluídos na base e incluídos nos dois saldos na sensibilidade. Goodwill sintético = 10% do capital empregado em cada saldo; excluí-lo reduz apenas o denominador do ROCE. Nenhum resultado representa dados financeiros reais.') ])))
        content.append(panel('Catálogo de fontes oficiais',html.Div([html.A([html.Strong(c),html.Span(' Relações com investidores ↗')],href=url,target='_blank',rel='noopener noreferrer',className='source-link') for c,url in data.SOURCES.items()])))
        content.append(panel('Câmbio · fonte aprovada',html.Div([html.P('Fonte oficial: Bacen · média trimestral da PTAX venda diária de fechamento para fluxos. BRL→USD por divisão pela cotação R$/USD; converter trimestre antes da soma LTM.'),html.A('Consultar publicação oficial ↗',href=RULES['fx']['source_url'],target='_blank',rel='noopener noreferrer')])))
        content.append(panel('Imposto operacional · OPEN-03 aprovada',html.Div([html.P(RULES['operating_tax']['basis']),html.Ol([html.Li(step['description']) for step in RULES['operating_tax']['hierarchy']]),html.P('Aprovação metodológica em 05/10/2026. Fórmula implementada com cenário sintético; dados reais e reconciliação permanecem pendentes.') ])))
        content.append(panel('Rastreabilidade',html.Div('Documento → localização → fato bruto → ajustes → normalização → cálculo → métrica → visual',className='formula')))
        content.append(panel('Goodwill e híbridos · política aprovada',html.Div([html.P(RULES['capital_policy']['goodwill_sensitivity']),html.P(RULES['capital_policy']['hybrids_base']),html.P(RULES['capital_policy']['hybrids_sensitivity'])])))
        content.append(panel('Aprovação de dados · PoC',html.Div([html.P('Reconciliação: maior entre US$ 1 milhão, 0,1% do total de referência e arredondamento documentado. Variação superior a 30% gera alerta; base anterior zero exige revisão separada.'),html.P('Um responsável aprova mapeamentos, exceções e publicação. Valores não comparáveis preservam número e justificativa, com destaque visual, e são excluídos das séries regulares.') ])))
    elif key=='rules':
        content.append(panel('Regras financeiras versionadas',table([{'KPI':v['name'],'versão':RULES['version'],'fórmula':v['formula']} for v in RULES['metrics'].values()])))
        content.append(panel('Decisões metodológicas',table([{'ID':k,'decisão':v,'estado':RULES['operating_tax']['status'] if k=='OPEN-03' else RULES['fx']['status'] if k=='OPEN-02' else RULES['capital_policy']['status'] if k=='OPEN-05' else 'PENDENTE'} for k,v in [('OPEN-01','Prazo de entrega'),('OPEN-02','Fonte oficial de câmbio'),('OPEN-03','Hierarquia de imposto operacional'),('OPEN-04','Meta de desempenho em VPS'),('OPEN-05','Goodwill e híbridos'),('OPEN-06','Aprovação das cores por empresa')]])))
        content.append(panel('Restatements',html.P('Nenhuma revisão financeira aprovada. Uploads novos são preservados e aguardam revisão; não sobrescrevem documentos anteriores.')))
    elif key=='upload':
        content.append(panel('Preservar documento original',html.Div([html.P('PDF, XLSX, CSV ou HTML · até 20 MB. O upload preserva o original e registra sua origem para revisão. Não publica valores automaticamente.'),html.Div([dcc.Dropdown(list(data.COMPANIES),'Petrobras',id='upload-company',clearable=False),dcc.Dropdown(data.PERIODS,period,id='upload-period',clearable=False)],className='two-col'),dcc.Input(id='source-url',placeholder='URL pública original (https://...)',type='url',className='text-input'),dcc.Input(id='locator',placeholder='Localização: página, tabela, linha ou célula',className='text-input'),dcc.Upload(id='upload-file',children=html.Div(['↑',html.H3('Selecione ou arraste um documento'),html.P('O original será preservado com hash SHA-256')]),className='upload-zone',multiple=False),html.Div(id='upload-result',role='status') ])))
        docs=data.documents(); content.append(panel('Histórico de documentos',table(docs.astype(str).to_dict('records'))))
    return [title,'Compare empresas, acompanhe o ciclo e entenda o que sustenta a geração de valor.',content]+['nav-link active' if k==key else 'nav-link' for k,_,_ in NAV]

def fmt(value,suffix=''):
    return 'Indisponível' if value is None else f'{value:,.1f}'.replace(',','X').replace('.',',').replace('X','.')+suffix

def metric_quality(row, metric, view='standard'):
    key = 'reported_quality' if metric == 'roce' and view == 'reported' else 'quality'
    return row.get(key, {}).get(metric, {})


def metric_cell(row, metric, view):
    quality = metric_quality(row, metric, view)
    non_comparable = quality.get('status') == 'NAO_COMPARAVEL'
    value = row['reported_roce'] if metric == 'roce' and view == 'reported' else row[metric]
    suffix = {'roce':'%','cfo':' mi','leverage':'x','capex':'%','distribution':'%'}[metric]
    return html.Div([
        html.Span(RULES['metrics'][metric]['name']),
        html.Strong(fmt(value, suffix)),
        html.Div([html.Strong('⚠ NÃO COMPARÁVEL'), html.Span(quality['reason'])],
                 className='comparability-warning') if non_comparable else None,
    ], className='metric-row non-comparable' if non_comparable else 'metric-row',
       title=RULES['metrics'][metric]['formula']+' · '+RULES['metrics'][metric]['note'])


def comparison(rows,view):
    return html.Div([html.Div([
        html.Div([html.Span(r['company'][0],className='company-monogram',
                  style={'backgroundColor':data.COMPANIES[r['company']][0]}),
                  html.Div([html.H4(r['company']),html.Small(data.COMPANIES[r['company']][1])])],className='company-heading'),
        *[metric_cell(r,k,view) for k in RULES['metrics']],
        html.A('Definições e fontes ↗',href='/method',className='company-source')
    ],className='company-card') for r in rows],className='company-grid')


def cash_table(rows):
    records, flagged = [], []
    dependencies = {'FCO':['cfo'], 'CAPEX':['cfo','capex'], 'FCL':['cfo','capex'],
                    'distribuições':['cfo','distribution'], 'caixa residual':['cfo','capex','distribution']}
    for index, row in enumerate(rows):
        record = {'empresa':row['company'],'FCO':fmt(row['cfo']),
                  'CAPEX':fmt((row['cfo'] or 0)*(row['capex'] or 0)/100),
                  'FCL':fmt(row['fcf']),
                  'distribuições':fmt((row['cfo'] or 0)*(row['distribution'] or 0)/100),
                  'caixa residual':fmt(row['residual'])}
        for key, metrics in dependencies.items():
            reasons = [metric_quality(row,m)['reason'] for m in metrics
                       if metric_quality(row,m).get('status') == 'NAO_COMPARAVEL']
            if reasons:
                record[key] += ' · ⚠ NÃO COMPARÁVEL: ' + '; '.join(dict.fromkeys(reasons))
                flagged.append((index,key))
        records.append(record)
    return table(records,column_labels={'FCO':'FCO','CAPEX':'CAPEX','FCL':'FCL'},flagged_cells=flagged)

def cash_chart(rows,colors):
    fig=go.Figure()
    for label,key,color in [('FCO','cfo','#008542'),('FCL','fcf','#00a397'),('Caixa residual','residual','#b9c9bd')]: fig.add_bar(name=label,x=[r['company'] for r in rows],y=[r[key]/1000 if r[key] is not None and not any(metric_quality(r,m).get('status') == 'NAO_COMPARAVEL' for m in {'cfo':['cfo'],'fcf':['cfo','capex'],'residual':['cfo','capex','distribution']}[key]) else None for r in rows],marker_color=color,marker_cornerradius=4,hovertemplate='%{x}<br>%{y:.2f} US$ bi<extra>'+label+'</extra>')
    fig.update_layout(barmode='group',bargap=.35); return graph(fig)

@app.callback(Output('metric-chart','children'),Input('metric','value'),Input('companies','value'),Input('period','value'),Input('view','value'),Input('sensitivities','value'))
def metric_chart(metric,companies,period,view,sensitivities):
    fig=go.Figure()
    warnings=[]
    for company in companies or []:
        vals=[]; periods=[p for p in data.PERIODS if p<=period]
        for p in periods:
            row=data.metrics(p,[company],'include_leases' in (sensitivities or []),exclude_goodwill='exclude_goodwill' in (sensitivities or []))[0]
            quality=metric_quality(row,metric,view)
            value=row['reported_roce'] if metric=='roce' and view=='reported' else row[metric]
            if quality.get('status') == 'NAO_COMPARAVEL':
                warnings.append(html.Li(f"{company} · {p}: {fmt(value)} {RULES['metrics'][metric]['unit']} — {quality['reason']}"))
                vals.append(None)
            else:
                vals.append(value)
        fig.add_scatter(x=periods,y=vals,name=company,mode='lines+markers',connectgaps=False,line=dict(color=data.COMPANIES[company][0],width=3),marker=dict(size=7))
    return panel(RULES['metrics'][metric]['name'],html.Div([graph(fig),html.Div([html.Strong('⚠ NÃO COMPARÁVEL — pontos excluídos da série'),html.Ul(warnings)],className='non-comparable') if warnings else None]),RULES['metrics'][metric]['formula']+' · '+RULES['metrics'][metric]['unit'])

@app.callback(Output('upload-result','children'),Input('upload-file','contents'),State('upload-file','filename'),State('upload-company','value'),State('upload-period','value'),State('source-url','value'),State('locator','value'),prevent_initial_call=True)
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

if __name__=='__main__': app.run(host='127.0.0.1',port=int(os.environ.get('PORT','8050')),debug=False)
