"""Sourced operational production mix, independent of financial KPI sensitivities."""
import json
import os
import re
from decimal import Decimal
from pathlib import Path


def production_dataset():
    return json.loads((Path(os.environ.get('RADAR_PROJECT_DIR', '.')) / 'config/production-mix.json').read_text())


def calculate_mix(record):
    """Use volumes from the same period/scope; never infer missing gas as zero."""
    liquids = Decimal(str(record['liquids_kbd']))
    gas = Decimal(str(record['gas_kboed']))
    reported = Decimal(str(record['total_reported_kboed']))
    if not all(v.is_finite() for v in (liquids, gas, reported)) or min(liquids, gas) < 0 or reported <= 0:
        raise ValueError('Volumes de produção inválidos.')
    total = liquids + gas
    if total <= 0 or abs(total - reported) > Decimal('2'):
        raise ValueError('Componentes não conciliam com a produção divulgada (tolerância: 2 kboe/d por arredondamento).')
    share = gas / total * 100
    return dict(record, gas_share_pct=float(share), liquids_share_pct=float(100-share),
                total_calculated_kboed=float(total), reconciliation_delta_kboed=float(total-reported))


def production_mix(period, companies, allowed_periods=None):
    if allowed_periods is not None and period not in allowed_periods:
        return []
    dataset = production_dataset()
    result = []
    seen = set()
    for record in dataset['records']:
        if not re.fullmatch(r'\d{4}Q[1-4]', record['period']):
            raise ValueError('Período de produção inválido.')
        identity = (record['company'], record['period'])
        if identity in seen:
            raise ValueError('Produção duplicada para empresa/trimestre.')
        seen.add(identity)
        if record['period'] == period and record['company'] in companies:
            source = dataset['sources'][record['source']]
            result.append(dict(calculate_mix(record), source_url=source['url'],
                               source_hash=source['sha256'], status=dataset['status']))
    return sorted(result, key=lambda r: companies.index(r['company']))
