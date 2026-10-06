"""Common, unit-elastic cash scenario; not an economic oil-price breakeven."""
from datetime import date, timedelta
from decimal import Decimal
from radar.ingestion.production import production_mix
from radar.ingestion.refining import refining_snapshot

METHOD = 'Brent de equilíbrio estimado = Brent spot médio LTM − caixa LTM / volume de líquidos LTM. Orgânico: caixa = FCO − CAPEX. Após distribuições: caixa = FCO − CAPEX − dividendos e recompras. Cada US$ 1/b de variação no Brent altera o FCO em US$ 1 por barril de líquidos produzido; demais fatores constantes.'
LIMITATION = 'Proxy de cenário, não breakeven econômico efetivo. Ignora resposta de impostos, royalties, gás, refino, trading, preços realizados e volumes ao Brent. Mantém as ressalvas das bases financeiras e de produção; Petrobras usa líquidos Brasil com caixa consolidado. Valores negativos são preservados, sem interpretação como preço viável de petróleo.'


def estimate(brent, volume_million_bbl, cfo, capex, distribution):
    if brent is None or volume_million_bbl is None or cfo is None or capex is None:
        return dict(organic=None,after_distribution=None)
    b,v,f,c=map(lambda x:Decimal(str(x)),(brent,volume_million_bbl,cfo,capex))
    if not all(x.is_finite() for x in (b,v,f,c)) or v<=0:
        return dict(organic=None,after_distribution=None)
    organic=b-(f-c)/v
    after=None if distribution is None else organic+Decimal(str(distribution))/v
    return dict(organic=float(organic),after_distribution=float(after) if after is not None else None)


def cash_breakeven(period, rows):
    end=int(period[:4])*4+int(period[-1])-1
    window=[f'{i//4}Q{i%4+1}' for i in range(end-3,end+1)]
    bounds=[]
    for p in window:
        y,q=int(p[:4]),int(p[-1]);start=date(y,3*q-2,1)
        stop=date(y+1,1,1) if q==4 else date(y,3*q+1,1)
        bounds.append((p,start,stop))
    snapshot=refining_snapshot();prices=snapshot['series']['brent']['prices'];daily=[];eligible=True
    for _,start,stop in bounds:
        values=[Decimal(str(v)) for stamp,v in prices.items() if str(start)<=stamp<str(stop)]
        eligible &= len(values)>=40 and snapshot['start']<=str(start) and snapshot['end']>=str(stop-timedelta(days=1))
        daily.extend(values)
    brent=float(sum(daily)/len(daily)) if eligible and daily else None
    result=[]
    for row in rows:
        volume=Decimal(0);missing=[];sources=[]
        for p,start,stop in bounds:
            records=production_mix(p,[row['company']])
            if not records:missing.append(p);continue
            record=records[0];volume+=Decimal(str(record['liquids_kbd']))*(stop-start).days/1000
            sources.append(record)
        v=float(volume) if not missing and volume>0 else None
        values=estimate(brent,v,row['cfo'],None if row['fcf'] is None or row['cfo'] is None else row['cfo']-row['fcf'],None if row['fcf'] is None or row['residual'] is None else row['fcf']-row['residual'])
        reasons=[LIMITATION]
        for key in ('cfo','capex','distribution'):
            reason=row.get('quality',{}).get(key,{}).get('reason')
            if reason:reasons.append(reason)
        if missing:reasons.append('Produção ausente: '+', '.join(missing))
        if brent is None:reasons.append('Brent spot sem quatro trimestres completos com pelo menos 40 observações por trimestre.')
        result.append(dict(company=row['company'],brent=brent,volume=v,sources=sources,reason='; '.join(dict.fromkeys(reasons)),**values))
    return result
