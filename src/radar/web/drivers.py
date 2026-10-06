"""Demonstration context figures; never presented as published market data."""
import json
from pathlib import Path
import os
import plotly.graph_objects as go


def financial_periods(period, companies, dataset):
    from radar import data
    frame=data.facts(dataset)
    if frame.empty or not companies:return []
    frame=frame[frame.company.isin(companies) & (frame.period<=period)]
    flows=[k for k in ('cfo','capex','ebitda','nopat_disclosed','ebit_adjusted') if k in frame]
    frame=frame[frame[flows].notna().any(axis=1)] if flows else frame.iloc[:0]
    if frame.empty:return []
    return [p for p in data.periods() if frame.period.min()<=p<=frame.period.max()]


def figures(period, companies, colors, allowed_periods=None):
    dataset=json.loads((Path(os.environ.get('RADAR_PROJECT_DIR','.'))/'config/drivers-demo.json').read_text())
    periods=[p for p in dataset['periods'] if p<=period and (allowed_periods is None or p in allowed_periods)]
    indices=[dataset['periods'].index(p) for p in periods]
    result={}
    for key, series, title, color in [
        ('brent','brent','US$/barril','#008542'),
        ('fx','fx_brl_usd','R$/US$','#006298')]:
        fig=go.Figure(go.Scatter(x=periods,y=[dataset[series][i] for i in indices],
                                mode='lines+markers',name='Cenário sintético',line=dict(color=color,width=3),
                                hovertemplate='%{x}<br>%{y:.2f} '+title+'<extra>DEMONSTRAÇÃO</extra>'))
        fig.update_yaxes(title_text=title,rangemode='tozero')
        result[key]=fig
    gas=go.Figure(); margin=go.Figure()
    for company in companies:
        if period in dataset['periods']:
            share=dataset['gas_share_pct'][company][dataset['periods'].index(period)]
            gas.add_bar(x=[company],y=[share],name=company+' · gás',marker_color='#dce7df',
                        text=[f'{share}% gás'],textposition='inside',
                        hovertemplate='%{x}<br>Gás: %{y:.1f}% da produção em boe<extra>DEMONSTRAÇÃO</extra>',showlegend=False)
            gas.add_bar(x=[company],y=[100-share],name=company+' · líquidos',marker_color=colors[company],
                        text=[f'{100-share}% líquidos'],textposition='inside',
                        hovertemplate='%{x}<br>Líquidos: %{y:.1f}% da produção em boe<extra>DEMONSTRAÇÃO</extra>',showlegend=False)
        margin.add_scatter(x=periods,y=[dataset['refining_margin_usd_bbl'][company][i] for i in indices],
                           name=company,mode='lines+markers',line=dict(color=colors[company],width=3),
                           hovertemplate='%{x}<br>%{y:.2f} US$/barril<extra>%{fullData.name} · demonstração</extra>')
    if period not in dataset['periods']:
        gas.add_annotation(text='Mix indisponível para este trimestre.',xref='paper',yref='paper',x=.5,y=.5,showarrow=False)
    gas.update_layout(barmode='stack'); gas.update_yaxes(title_text='% da produção em boe',range=[0,100])
    margin.update_yaxes(title_text='US$/barril',rangemode='tozero')
    if not companies:
        for fig in (gas,margin):
            fig.add_annotation(text='Selecione uma empresa para visualizar.',xref='paper',yref='paper',x=.5,y=.5,showarrow=False)
    result.update(gas=gas,margin=margin)
    return result


def real_figures(period, companies, colors, allowed_periods=None):
    """Real context only; missing series stay empty, never reuse demo context."""
    from decimal import Decimal
    from radar.ingestion.pipeline import snapshots, period_dates
    from radar import data
    source=snapshots()
    result={key:go.Figure() for key in ('brent','fx','gas','margin')}
    for key,symbol,unit in [('brent','BZ=F','US$/barril'),('fx',None,'R$/US$')]:
        periods=[];values=[]
        for p in (data.periods() if allowed_periods is None else allowed_periods):
            if p>period:continue
            start,end=period_dates(p)
            eligible=[s for s in source if (s['provider']=='Yahoo' and s.get('symbol')==symbol) or (key=='fx' and s['provider']=='Bacen')]
            rates={}
            for snapshot in eligible:
                if key=='fx':
                    if snapshot['start']>str(start) or snapshot['end']<str(end):continue
                    rates.update({d:v for d,v in snapshot['rates'].items() if str(start)<=d<=str(end)})
                else:
                    rates.update({v['date']:v['close'] for v in snapshot.get('points',[]) if str(start)<=v['date']<=str(end)})
            periods.append(p)
            values.append(float(sum(Decimal(v) for v in rates.values())/len(rates)) if rates else None)
        result[key].add_scatter(x=periods,y=values,mode='lines+markers',connectgaps=False,name='Yahoo · futuro contínuo BZ=F' if key=='brent' else 'Bacen · PTAX venda')
        result[key].update_yaxes(title_text=unit)
        if not any(v is not None for v in values):
            result[key].add_annotation(text='Série real ainda não coletada.',xref='paper',yref='paper',x=.5,y=.5,showarrow=False)
    from radar.ingestion.production import production_mix
    mix=production_mix(period, companies, allowed_periods)
    for row in mix:
        company=row['company']
        for field,label,color in [('liquids_share_pct','Líquidos',colors[company]),('gas_share_pct','Gás','#dce7df')]:
            value=row[field]
            result['gas'].add_bar(x=[company],y=[value],name=company+' · '+label,
                marker=dict(color=color,line=dict(color=colors[company],width=1)),
                text=[f'{value:.1f}%'],textposition='inside',showlegend=False,
                customdata=[[period,row['scope']]],
                hovertemplate='%{x}<br>%{customdata[0]} · %{customdata[1]}<br>'+label+': %{y:.1f}%<br>NÃO-COMPARÁVEL<extra></extra>')
    result['gas'].update_layout(barmode='stack')
    result['gas'].update_yaxes(title_text='% da produção em boe',range=[0,100])
    missing=[c for c in companies if c not in [r['company'] for r in mix]]
    if missing or not companies:
        result['gas'].add_annotation(text=('Mix indisponível em '+period+': '+', '.join(missing)) if missing else 'Selecione uma empresa para visualizar.',
            xref='paper',yref='paper',x=.5,y=1.08,showarrow=False)
    from radar.ingestion.refining import refining_snapshot, quarterly_margins
    margins=quarterly_margins(refining_snapshot(),[p for p in (data.periods() if allowed_periods is None else allowed_periods) if p<=period])
    result['margin'].add_scatter(x=[r['period'] for r in margins],y=[r['value'] for r in margins],
        mode='lines+markers',connectgaps=False,name='EIA · Brent–Golfo dos EUA 3–2–1',
        customdata=[[r['observations'],r['excluded_dates']] for r in margins],
        hovertemplate='%{x}<br>%{y:.2f} US$/barril<br>%{customdata[0]} datas comuns · %{customdata[1]} excluídas<extra>Benchmark de mercado</extra>')
    result['margin'].update_yaxes(title_text='US$/barril')
    if not any(r['value'] is not None for r in margins):
        result['margin'].add_annotation(text='Benchmark indisponível para o período selecionado.',xref='paper',yref='paper',x=.5,y=.5,showarrow=False)
    return result
