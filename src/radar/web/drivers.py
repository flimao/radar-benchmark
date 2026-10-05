"""Demonstration context figures; never presented as published market data."""
import json
from pathlib import Path
import os
import plotly.graph_objects as go


def figures(period, companies, colors):
    dataset=json.loads((Path(os.environ.get('RADAR_PROJECT_DIR','.'))/'config/drivers-demo.json').read_text())
    periods=[p for p in dataset['periods'] if p<=period]
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
        share=dataset['gas_share_pct'][company][dataset['periods'].index(period)]
        gas.add_bar(x=[company],y=[share],name=company+' · gás',marker_color=colors[company],
                    text=[f'{share}% gás'],textposition='inside',
                    hovertemplate='%{x}<br>Gás: %{y:.1f}% da produção em boe<extra>DEMONSTRAÇÃO</extra>',showlegend=False)
        gas.add_bar(x=[company],y=[100-share],name=company+' · líquidos',marker_color='#dce7df',
                    text=[f'{100-share}% líquidos'],textposition='inside',
                    hovertemplate='%{x}<br>Líquidos: %{y:.1f}% da produção em boe<extra>DEMONSTRAÇÃO</extra>',showlegend=False)
        margin.add_scatter(x=periods,y=[dataset['refining_margin_usd_bbl'][company][i] for i in indices],
                           name=company,mode='lines+markers',line=dict(color=colors[company],width=3),
                           hovertemplate='%{x}<br>%{y:.2f} US$/barril<extra>%{fullData.name} · demonstração</extra>')
    gas.update_layout(barmode='stack'); gas.update_yaxes(title_text='% da produção em boe',range=[0,100])
    margin.update_yaxes(title_text='US$/barril',rangemode='tozero')
    if not companies:
        for fig in (gas,margin):
            fig.add_annotation(text='Selecione uma empresa para visualizar.',xref='paper',yref='paper',x=.5,y=.5,showarrow=False)
    result.update(gas=gas,margin=margin)
    return result
