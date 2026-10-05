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


def balance_ptax_sale(balance_date, published_rates):
    """Return (publication date, sale rate) for the latest date <= balance date.

    Input mapping uses ISO dates and one validated closing PTAX sale per day.
    No future rate or invented fallback is permitted.
    """
    from datetime import date
    target = date.fromisoformat(balance_date)
    eligible = [(date.fromisoformat(day), rate) for day, rate in published_rates.items()
                if date.fromisoformat(day) <= target]
    if not eligible:
        return None
    publication, raw_rate = max(eligible, key=lambda item: item[0])
    rate = Decimal(str(raw_rate))
    if not rate.is_finite() or rate <= 0:
        raise ValueError('PTAX venda de fechamento deve ser finita e positiva.')
    return publication.isoformat(), rate


def convert_balance_brl_to_usd(value, balance_date, published_rates):
    selected = balance_ptax_sale(balance_date, published_rates)
    if selected is None:
        return None
    publication, rate = selected
    return {'value_usd': brl_to_usd(value, rate), 'balance_date': balance_date,
            'fx_publication_date': publication, 'brl_per_usd': rate,
            'fallback_previous_publication': publication != balance_date}
