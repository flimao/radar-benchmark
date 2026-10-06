"""Common Brent/US Gulf Coast 3-2-1 market benchmark, not company realised margin."""
import argparse
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
from html import unescape
import json
import os
from pathlib import Path
import re

SERIES = {
    'brent': ('RBRTED', 'Europe Brent Spot Price FOB', 'USD/bbl'),
    'gasoline': ('EER_EPMRU_PF4_RGC_DPGD', 'U.S. Gulf Coast Conventional Gasoline Regular Spot Price FOB', 'USD/US gallon'),
    'diesel': ('EER_EPD2DXL0_PF4_RGC_DPGD', 'U.S. Gulf Coast Ultra-Low Sulfur No 2 Diesel Spot Price', 'USD/US gallon'),
}
MONTHS = {m:i+1 for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
METHOD = 'Margem indicativa comum Brent–Golfo dos EUA 3–2–1 = (2 × gasolina × 42 + diesel × 42) / 3 − Brent spot, em US$/barril. Média aritmética trimestral das margens diárias nas datas com os três preços disponíveis.'
LIMITATION = 'Benchmark comum de mercado, não margem realizada das empresas. Combina petróleo Brent europeu com derivados do Golfo dos EUA. Não inclui frete, diferencial de qualidade do petróleo, energia, pessoal, manutenção, impostos, trading ou rendimentos específicos das refinarias. Não permite ordenar a eficiência de refino das empresas.'


def parse_eia_daily(html, start, end):
    """Preserve weekday position, including blank holiday cells and year crossings."""
    prices={}
    for match in re.finditer(r"<td\s+class=['\"]B6['\"]>(.*?)</td>(.*?)</tr>", html, re.S|re.I):
        label=unescape(re.sub('<[^>]+>', '', match[1])).strip()
        stamp=re.match(r'(\d{4})\s+([A-Z][a-z]{2})-\s*(\d{1,2})\s+to', label)
        if not stamp:continue
        monday=date(int(stamp[1]),MONTHS[stamp[2]],int(stamp[3]))
        if monday.weekday()!=0:raise ValueError('Linha diária EIA não inicia na segunda-feira.')
        cells=re.findall(r"<td\s+class=['\"]B3['\"]>(.*?)</td>",match[2],re.S|re.I)
        if len(cells)!=5:raise ValueError('Linha diária EIA sem cinco dias úteis.')
        for offset,cell in enumerate(cells):
            day=monday+timedelta(days=offset)
            if not start<=day<=end:continue
            value=unescape(re.sub('<[^>]+>', '', cell)).strip()
            if value in ('','-','--','NA','W'):continue
            amount=Decimal(value)
            if not amount.is_finite() or amount<=0:raise ValueError('Preço spot inválido.')
            if str(day) in prices:raise ValueError('Data EIA duplicada.')
            prices[str(day)]=str(amount)
    if not prices:raise ValueError('Nenhum preço EIA encontrado no intervalo.')
    return prices


def crack_spread(brent, gasoline, diesel):
    values=[Decimal(str(v)) for v in (brent,gasoline,diesel)]
    if not all(v.is_finite() and v>0 for v in values):raise ValueError('Preço spot inválido.')
    b,g,d=values
    return (2*g*42+d*42)/3-b


def quarterly_margins(snapshot, periods):
    groups=defaultdict(list);union=defaultdict(set)
    for key in SERIES:
        for stamp in snapshot['series'][key]['prices']:
            day=date.fromisoformat(stamp)
            union[f'{day.year}Q{(day.month-1)//3+1}'].add(stamp)
    common=set.intersection(*(set(snapshot['series'][key]['prices']) for key in SERIES))
    for stamp in sorted(common):
        day=date.fromisoformat(stamp);period=f'{day.year}Q{(day.month-1)//3+1}'
        groups[period].append(crack_spread(*(snapshot['series'][key]['prices'][stamp] for key in SERIES)))
    result=[]
    for period in periods:
        values=groups[period];available=len(union[period]);coverage=len(values)/available if available else 0
        # Require a full collection window; never show partial quarters as full-quarter means.
        year=int(period[:4]);quarter=int(period[-1]);start=date(year,quarter*3-2,1)
        next_start=date(year+1,1,1) if quarter==4 else date(year,quarter*3+1,1)
        full=snapshot['start']<=str(start) and snapshot['end']>=str(next_start-timedelta(days=1))
        eligible=full and len(values)>=40 and coverage>=.9
        result.append(dict(period=period,value=float(sum(values)/len(values)) if eligible else None,
                           observations=len(values),available_dates=available,excluded_dates=available-len(values),coverage_pct=coverage*100))
    return result


def refining_snapshot():
    return json.loads((Path(os.environ.get('RADAR_PROJECT_DIR','.'))/'config/refining-market.json').read_text())


def collect(start, end, output, archive):
    import httpx
    if start>end:raise ValueError('Intervalo invertido.')
    archive.mkdir(parents=True,exist_ok=True)
    snapshot=dict(schema_version=1,provider='EIA',collected_at=datetime.now(timezone.utc).isoformat(),
                  start=str(start),end=str(end),method=METHOD,limitation=LIMITATION,series={})
    for key,(code,title,unit) in SERIES.items():
        url=f'https://www.eia.gov/dnav/pet/hist/{code}.htm'
        response=httpx.get(url,timeout=60,follow_redirects=True);response.raise_for_status()
        body=response.content;html=response.text
        if title not in unescape(re.sub('<[^>]+>',' ',html)):
            raise ValueError('Título da série EIA não corresponde à série esperada.')
        digest=hashlib.sha256(body).hexdigest();(archive/(digest+'.html')).write_bytes(body)
        snapshot['series'][key]=dict(code=code,title=title,unit=unit,url=url,sha256=digest,prices=parse_eia_daily(html,start,end))
    # Write only after all three sources validate; an interrupted collection preserves the previous snapshot.
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_suffix('.json.tmp');temporary.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n');temporary.replace(output)
    return snapshot


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Coletar preços EIA para benchmark de refino comum.')
    parser.add_argument('--start',type=date.fromisoformat,required=True)
    parser.add_argument('--end',type=date.fromisoformat,required=True)
    parser.add_argument('--output',type=Path,default=Path(os.environ.get('RADAR_PROJECT_DIR','.'))/'config/refining-market.json')
    parser.add_argument('--archive',type=Path,default=Path(os.environ.get('RADAR_DATA_DIR','.'))/'data/context/eia')
    args=parser.parse_args();collect(args.start,args.end,args.output,args.archive)
