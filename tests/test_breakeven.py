from radar.ingestion.breakeven import estimate

def test_cash_scenario_units_and_distributions():
    assert estimate(75,600,30000,18000,9000)==dict(organic=55.,after_distribution=70.)
    assert estimate(75,600,10000,18000,0)['organic']>75
    assert estimate(20,100,10000,0,0)['organic']==-80

def test_missing_inputs_do_not_become_zero():
    assert estimate(75,None,30000,18000,9000)['organic'] is None
    assert estimate(75,600,30000,18000,None)==dict(organic=55.,after_distribution=None)
    assert estimate(75,0,30000,18000,9000)['organic'] is None

def test_uses_distribution_cash_not_distribution_ratio():
    from radar import data
    from radar.ingestion.breakeven import cash_breakeven
    row=dict(company='Chevron',cfo=30000,fcf=12000,residual=3000,distribution=30,quality={})
    result=cash_breakeven('2025Q4',[row])[0]
    assert result['volume']>0
    assert abs((result['after_distribution']-result['organic'])*result['volume']-9000)<1e-8
