"""Administration UI for preparation, documented approval and publication."""
import base64
import json
from dash import html, dcc, Input, Output, State, no_update
from radar.ingestion import pipeline as pipe


def controls(panel, table):
    history=pipe.batches()
    return [panel('Preparar dados reais',html.Div([
        html.P('Envie um mapeamento JSON com hashes dos documentos já carregados. A preparação extrai, normaliza e concilia; os valores só aparecem na base real após revisão e publicação.'),
        html.Div([html.Div(['Selecionar mapeamento JSON ',html.Small('(bloqueado pela SI Petrobras)',className='upload-blocked-note')],className='upload-zone upload-disabled',title='A Segurança da Informação da Petrobras bloqueia automaticamente sites que ofereçam funcionalidade de upload de arquivos.',**{'aria-disabled':'true'}),dcc.Store(id='mapping-upload')]),
        html.Div(id='mapping-result',role='status'),
    ])),panel('Revisar e publicar',html.Div([
        dcc.Dropdown([{'label':f"{r['company']} · {r['mapping_version']} · {r['status']}",'value':r['id']} for r in history.to_dict('records')],id='ingestion-batch',placeholder='Selecione um lote'),
        html.Div(id='batch-report'),
        dcc.Input(id='reviewer',placeholder='Responsável pela revisão',className='text-input'),
        dcc.Textarea(id='review-note',placeholder='Justificativa da revisão, exceções e aprovação do mapeamento',className='text-input'),
        dcc.Checklist([{'label':'Aceitar os alertas de variação com a justificativa acima','value':'accept'}],[],id='accept-alerts'),
        html.Div([html.Button('Aprovar campos elegíveis',id='approve-batch',className='button'),html.Button('Publicar lote aprovado',id='publish-batch',className='button')],className='ingestion-actions'),
        html.Div(id='review-result',role='status'),
    ])),panel('Coletar séries de APIs',html.Div([
        html.P('PTAX é a fonte aprovada para conversão BRL/USD. Yahoo é contexto de mercado, sujeito à disponibilidade; não substitui a DFC nem a PTAX.'),
        dcc.Dropdown([{'label':'PTAX venda · Bacen','value':'PTAX'},{'label':'Brent futuro · Yahoo (BZ=F)','value':'BZ=F'},{'label':'Câmbio de mercado · Yahoo (BRL=X)','value':'BRL=X'}],'PTAX',id='api-series',clearable=False),
        html.Div([dcc.Input(id='api-start',type='text',value='2025-01-01',placeholder='AAAA-MM-DD',className='text-input'),dcc.Input(id='api-end',type='text',value='2025-12-31',placeholder='AAAA-MM-DD',className='text-input')],className='two-col'),
        html.Button('Coletar e preservar série',id='fetch-api',className='button'),html.Div(id='api-result',role='status'),
    ])),panel('Histórico de lotes',table(history.astype(str).to_dict('records')))]


def callbacks(app, panel, table, badge):
    @app.callback(Output('mapping-result','children'),Output('ingestion-batch','options'),Input('mapping-upload','data'),prevent_initial_call=True)
    def prepare(contents):
        if not contents:return no_update,no_update
        try:
            content=base64.b64decode(contents.split(',',1)[1],validate=True)
            if len(content)>1024*1024:raise ValueError('Mapeamento excede 1 MB.')
            manifest=json.loads(content)
            if any('path' in d for d in manifest.get('documents',[])):
                raise ValueError('Na interface use hash do documento carregado. Caminhos locais somente via CLI.')
            result=pipe.stage(manifest)
            history=pipe.batches().to_dict('records')
            return html.Div([badge(result['status']),html.P('Lote preparado: '+result['id'])]),[{'label':f"{r['company']} · {r['mapping_version']} · {r['status']}",'value':r['id']} for r in history]
        except Exception as exc:return html.P(str(exc),className='error'),no_update

    @app.callback(Output('batch-report','children'),Input('ingestion-batch','value'),Input('review-result','children'))
    def report(batch_id,_):
        if not batch_id:return html.P('Selecione um lote para ver os fatos e conciliações.')
        batch=pipe.get_batch(batch_id)
        report=batch['report']
        points=[{'período':p['period'],'campo':p['field'],'valor USD mi':p['value'],'estado':p['state'],
                 'comparabilidade':'COMPARÁVEL' if p['comparable'] else 'NÃO COMPARÁVEL','motivos':'; '.join(p['reasons']),'flags':', '.join(p['flags']),'locator':p['locator']} for p in report['points']]
        raw=[{'id':p['id'],'valor original':p['raw_value'],'moeda':p['currency'],'escala':p['scale'],'fonte':p['url'],'hash':p['hash'],'locator':p['locator']} for p in report['raw']]
        bridges=[{'ponte':p['id'],'diferença USD mi':p.get('difference_usd_million'),'tolerância USD mi':p.get('tolerance_usd_million'),'conciliado':p['passed'],'motivo':p.get('error',p['reason'])} for p in report['reconciliations']]
        return html.Div([badge(batch['status']),html.P('Responsável: '+(batch['reviewer'] or 'Aguardando revisão')),
                         html.H4('Pendências do mapeamento') if report.get('pending_components') else None,
                         table(report['pending_components']) if report.get('pending_components') else None,
                         html.H4('Componentes normalizados'),table(points),html.H4('Fatos originais'),table(raw),html.H4('Conciliações'),table(bridges),
                         html.Pre(json.dumps(report['errors'],ensure_ascii=False,indent=2)) if report['errors'] else None])

    @app.callback(Output('review-result','children'),Input('approve-batch','n_clicks'),Input('publish-batch','n_clicks'),State('ingestion-batch','value'),State('reviewer','value'),State('review-note','value'),State('accept-alerts','value'),prevent_initial_call=True)
    def review(_approve,_publish,batch_id,reviewer,note,alerts):
        from dash import ctx
        if not batch_id:return html.P('Selecione um lote.',className='error')
        try:
            if ctx.triggered_id=='approve-batch':result=pipe.approve(batch_id,reviewer or '',note or '',accept_alerts='accept' in (alerts or []))
            else:result=pipe.publish(batch_id)
            return html.P(result['status']+' · '+result['id']+'. Atualize a página para consultar a base real publicada.')
        except ValueError as exc:return html.P(str(exc),className='error')

    @app.callback(Output('api-result','children'),Input('fetch-api','n_clicks'),State('api-series','value'),State('api-start','value'),State('api-end','value'),prevent_initial_call=True)
    def fetch(_clicks,series,start,end):
        try:
            result=pipe.save_snapshot(pipe.fetch_ptax(start,end) if series=='PTAX' else pipe.fetch_yahoo(series,start,end))
            return html.Div([html.P('Série preservada. Use o hash PTAX no mapeamento para conversões. Séries Yahoo ficam disponíveis como contexto.'),html.Code(result['hash'])])
        except Exception as exc:return html.P('Série indisponível; nenhum valor foi inventado. '+str(exc),className='error')
