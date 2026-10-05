from decimal import Decimal
import json
from pathlib import Path
import pytest
from radar.fx import brl_to_usd, converted_ltm, mean_ptax_sales
from radar.quality import evaluate

POLICY = json.loads(Path('config/rules.json').read_text())['quality_policy']
CHECKS = {k:True for k in POLICY['required_checks']}


def test_fx_converts_before_ltm():
    assert brl_to_usd(500,5)==100
    assert mean_ptax_sales([4,6])==5
    assert converted_ltm([100]*4,[4,5,4,5])==90
    assert converted_ltm([100]*3,[5]*3) is None
    with pytest.raises(ValueError): brl_to_usd(100,0)


def test_quality_review_approval_alert_and_comparability():
    assert evaluate(CHECKS,POLICY)['publishable'] is False
    assert evaluate({},POLICY,approved=True)['state']=='BLOQUEADO'
    assert evaluate(CHECKS,POLICY,reference=1000,calculated=1001,approved=True)['state']=='APROVADO'
    assert evaluate(CHECKS,POLICY,reference=1000,calculated=1002,approved=True)['state']=='REVISAO'
    assert evaluate(CHECKS,POLICY,previous=100,current=131,approved=True)['publishable'] is False
    assert evaluate(CHECKS,POLICY,previous=100,current=131,approved=True,alert_accepted=True)['state']=='ALERTA'
    result=evaluate(CHECKS,POLICY,comparable=False,comparability_reason='Bases contábeis distintas',approved=True)
    assert result['comparability']=='NAO_COMPARAVEL'
    assert not result['eligible_for_comparison']
    with pytest.raises(ValueError): evaluate(CHECKS,POLICY,comparable=False)


def test_goodwill_sensitivity_missing_components():
    from radar.domain import roce
    rows=[dict(ebit_adjusted=100,operating_tax=20,capital_employed_open=1000,capital_employed_close=1000,goodwill_open=200,goodwill_close=200)]*4
    assert roce(rows)==32
    assert roce(rows,exclude_goodwill=True)==40
    assert roce([{**r,'goodwill_open':None} for r in rows],exclude_goodwill=True) is None

