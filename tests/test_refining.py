from datetime import date,timedelta
from decimal import Decimal
import pytest
from radar.ingestion.refining import crack_spread,parse_eia_daily,quarterly_margins,refining_snapshot


def test_units_and_negative_crack_spread():
    assert crack_spread(80,2,3) == Decimal('18')  # (168+126)/3 - 80
    assert crack_spread(120,2,3) == Decimal('-22')
    with pytest.raises(ValueError):crack_spread(80,float('nan'),3)


def test_parse_preserves_blanks_and_year_crossing():
    html="<tr><td class='B6'>2024 Dec-30 to Jan- 3</td>"+''.join("<td class='B3'>"+v+"</td>" for v in ['70','71','','73','74'])+'</tr>'
    prices=parse_eia_daily(html,date(2024,12,30),date(2025,1,3))
    assert prices == {'2024-12-30':'70','2024-12-31':'71','2025-01-02':'73','2025-01-03':'74'}


def test_quarter_mean_uses_only_common_dates_and_rejects_partial_window():
    days=[date(2024,1,1)+timedelta(days=i) for i in range(91)]
    prices={str(d):'2' for d in days if d.weekday()<5}
    snapshot=dict(start='2024-01-01',end='2024-03-31',series={k:{'prices':dict(prices)} for k in ('brent','gasoline','diesel')})
    snapshot['series']['brent']['prices']={d:'80' for d in prices}
    snapshot['series']['diesel']['prices']={d:'3' for d in prices}
    # One leg missing: that day's extreme Brent cannot bias the mean.
    stamp=next(iter(prices));snapshot['series']['brent']['prices'][stamp]='1000'
    del snapshot['series']['diesel']['prices'][stamp]
    row=quarterly_margins(snapshot,['2024Q1'])[0]
    assert row['value']==18
    assert row['excluded_dates']==1
    assert row['observations']==len(prices)-1
    snapshot['end']='2024-03-20'
    assert quarterly_margins(snapshot,['2024Q1'])[0]['value'] is None
    snapshot['end']='2024-03-31'
    snapshot['series']['diesel']['prices']={k:v for k,v in list(snapshot['series']['diesel']['prices'].items())[:20]}
    assert quarterly_margins(snapshot,['2024Q1'])[0]['value'] is None


def test_collected_history_covers_eight_quarters_without_backfill():
    snapshot=refining_snapshot()
    periods=[f'{y}Q{q}' for y in (2024,2025) for q in range(1,5)]
    rows=quarterly_margins(snapshot,periods)
    assert all(r['value'] is not None and r['coverage_pct']>=90 for r in rows)
    assert rows[0]['value']==pytest.approx(19.184852459)
    assert rows[-1]['value']==pytest.approx(19.744852459)
    assert quarterly_margins(snapshot,['2026Q1'])[0]['value'] is None
