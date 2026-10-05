"""Explicit BRL/USD normalization. Rates must come from validated Bacen publications."""
from decimal import Decimal


def brl_to_usd(value, brl_per_usd):
    value, rate = Decimal(str(value)), Decimal(str(brl_per_usd))
    if not value.is_finite() or not rate.is_finite() or rate <= 0:
        raise ValueError('Valor finito e cotação R$/USD positiva são obrigatórios.')
    return value / rate


def converted_ltm(quarterly_values, quarterly_rates):
    if len(quarterly_values) != 4 or len(quarterly_rates) != 4:
        return None
    if any(v is None for v in quarterly_values) or any(r is None for r in quarterly_rates):
        return None
    return sum(brl_to_usd(v, r) for v, r in zip(quarterly_values, quarterly_rates))


def mean_ptax_sales(published_daily_rates):
    """Mean of one closing PTAX sale rate per published day (no holiday fill)."""
    if not published_daily_rates:
        return None
    rates = [Decimal(str(rate)) for rate in published_daily_rates]
    if any(not rate.is_finite() or rate <= 0 for rate in rates):
        raise ValueError('Cotações PTAX venda devem ser finitas e positivas.')
    return sum(rates) / len(rates)
