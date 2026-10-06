from copy import deepcopy
import pytest
from radar.ingestion.production import calculate_mix, production_dataset, production_mix
from radar.web.drivers import real_figures


def test_all_company_quarters_reconcile_and_mix_sums_to_100():
    dataset=production_dataset()
    assert len(dataset['records']) == 32
    assert len({(r['company'],r['period']) for r in dataset['records']}) == 32
    for record in dataset['records']:
        mix=calculate_mix(record)
        assert mix['gas_share_pct']+mix['liquids_share_pct'] == pytest.approx(100)
        assert 0 < mix['gas_share_pct'] < 100
        assert abs(mix['reconciliation_delta_kboed']) <= 2
        assert record['source'] in dataset['sources']
        assert len(dataset['sources'][record['source']]['sha256']) == 64


def test_scopes_and_gas_classification_golden_values():
    mix={r['company']:r for r in production_mix('2025Q4',['Petrobras','TotalEnergies','Chevron','Shell'])}
    # Brazil only: do not include unallocated international production in the denominator.
    assert mix['Petrobras']['gas_share_pct'] == pytest.approx(577/(2504+577)*100)
    assert mix['Petrobras']['scope'] == 'Brasil'
    # Condensates and NGL remain in liquids, not in Total's broader gas business classification.
    assert mix['TotalEnergies']['gas_share_pct'] == pytest.approx((2545-1555)/2545*100)
    assert mix['Chevron']['gas_kboed'] == pytest.approx((3402+5514)/6)
    assert mix['Shell']['liquids_kbd'] == 128+1393+19  # IG + UP + oil sands
    assert all(r['status']=='NAO_COMPARAVEL' for r in mix.values())


def test_mix_does_not_backfill_missing_period_or_escape_kpi_range():
    assert production_mix('2026Q1',['Shell']) == []
    assert production_mix('2025Q4',['Shell'],['2025Q1']) == []
    assert production_mix('2025Q4',[]) == []
    assert [r['company'] for r in production_mix('2024Q1',['Shell','Petrobras'])] == ['Shell','Petrobras']


def test_invalid_production_cannot_be_presented_as_a_mix():
    record=deepcopy(production_dataset()['records'][0])
    record['gas_kboed']=-1
    with pytest.raises(ValueError):calculate_mix(record)
    record['gas_kboed']=999999
    with pytest.raises(ValueError):calculate_mix(record)
    record['gas_kboed']=float('nan')
    with pytest.raises(ValueError):calculate_mix(record)
    del record['gas_kboed']
    with pytest.raises(KeyError):calculate_mix(record)


def test_real_mix_chart_uses_real_volumes_and_selected_company(monkeypatch):
    import radar.ingestion.pipeline as pipeline
    monkeypatch.setattr(pipeline,'snapshots',lambda:[])
    fig=real_figures('2025Q4',['Petrobras'],{'Petrobras':'#008542'},['2025Q4'])['gas']
    assert len(fig.data)==2
    assert fig.data[0].x == ('Petrobras',)
    assert fig.data[0].y[0] == pytest.approx(2504/3081*100)
    assert fig.data[0].marker.color == '#008542'
    assert fig.data[1].marker.color == '#dce7df'
    assert fig.data[0].y[0]+fig.data[1].y[0] == pytest.approx(100)
    assert 'NÃO-COMPARÁVEL' in fig.data[0].hovertemplate
    missing=real_figures('2026Q1',['Petrobras'],{'Petrobras':'#008542'},['2026Q1'])['gas']
    assert len(missing.data)==0
