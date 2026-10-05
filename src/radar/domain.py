from decimal import Decimal

def ratio(numerator, denominator, factor=1):
    return None if denominator == 0 else Decimal(str(numerator)) / Decimal(str(denominator)) * Decimal(str(factor))

def ltm(values):
    return None if len(values) != 4 or any(v is None for v in values) else sum(Decimal(str(v)) for v in values)

def quarter(ytd, previous_ytd=0):
    return Decimal(str(ytd)) - Decimal(str(previous_ytd))

def roce(rows, leases=False):
    """Return a percentage; missing components or incomplete periods remain unavailable."""
    if len(rows) != 4:
        return None
    periods = [r.get('period') for r in rows]
    if any(periods):
        if not all(periods):
            return None
        indices = [int(p[:4]) * 4 + int(p[-1]) - 1 for p in periods]
        if any(b - a != 1 for a, b in zip(indices, indices[1:])):
            return None
    required = ['ebit_adjusted', 'operating_tax']
    if any(r.get(k) is None or not Decimal(str(r[k])).is_finite() for r in rows for k in required):
        return None
    start = rows[0].get('capital_employed_open')
    end = rows[-1].get('capital_employed_close')
    if start is None or end is None:
        return None
    start, end = Decimal(str(start)), Decimal(str(end))
    if leases:
        opening_leases = rows[0].get('leases_open')
        closing_leases = rows[-1].get('leases')
        if opening_leases is None or closing_leases is None:
            return None
        start += Decimal(str(opening_leases))
        end += Decimal(str(closing_leases))
    if not start.is_finite() or not end.is_finite():
        return None
    nopat = sum(Decimal(str(r['ebit_adjusted'])) - Decimal(str(r['operating_tax'])) for r in rows)
    return ratio(nopat, (start + end) / 2, 100)


def calculate(rows, leases=False):
    if len(rows) != 4:
        return {k: None for k in ('cfo','leverage','capex','distribution','fcf','residual','roce')}
    cfo = ltm([r['cfo'] for r in rows]); capex = ltm([r['capex'] for r in rows]); distribution = ltm([r['distribution'] for r in rows]); ebitda = ltm([r['ebitda'] for r in rows])
    debt = Decimal(str(rows[-1]['debt'])) + (Decimal(str(rows[-1]['leases'])) if leases else 0)
    return dict(cfo=cfo, leverage=ratio(debt, ebitda), capex=ratio(capex,cfo,100), distribution=ratio(distribution,cfo,100), fcf=cfo-capex, residual=cfo-capex-distribution, roce=roce(rows,leases))
