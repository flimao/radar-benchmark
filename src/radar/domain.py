from decimal import Decimal

def ratio(numerator, denominator, factor=1):
    return None if denominator == 0 else Decimal(str(numerator)) / Decimal(str(denominator)) * Decimal(str(factor))

def ltm(values):
    return None if len(values) != 4 or any(v is None for v in values) else sum(Decimal(str(v)) for v in values)

def quarter(ytd, previous_ytd=0):
    return Decimal(str(ytd)) - Decimal(str(previous_ytd))

def roce(rows, leases=False, exclude_goodwill=False):
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
    direct = all(r.get('nopat_disclosed') is not None and Decimal(str(r['nopat_disclosed'])).is_finite() for r in rows)
    if not direct and any(r.get(k) is None or not Decimal(str(r[k])).is_finite() for r in rows for k in required):
        return None
    start = rows[0].get('capital_employed_open')
    end = rows[-1].get('capital_employed_close')
    if start is None or end is None:
        return None
    start, end = Decimal(str(start)), Decimal(str(end))
    if exclude_goodwill:
        opening_goodwill = rows[0].get('goodwill_open')
        closing_goodwill = rows[-1].get('goodwill_close')
        if opening_goodwill is None or closing_goodwill is None:
            return None
        start -= Decimal(str(opening_goodwill))
        end -= Decimal(str(closing_goodwill))
    if leases:
        opening_leases = rows[0].get('leases_open')
        closing_leases = rows[-1].get('leases')
        if opening_leases is None or closing_leases is None:
            return None
        start += Decimal(str(opening_leases))
        end += Decimal(str(closing_leases))
    if not start.is_finite() or not end.is_finite():
        return None
    nopat = sum(Decimal(str(r['nopat_disclosed'])) for r in rows) if direct else sum(Decimal(str(r['ebit_adjusted'])) - Decimal(str(r['operating_tax'])) for r in rows)
    return ratio(nopat, (start + end) / 2, 100)


def calculate(rows, leases=False, exclude_goodwill=False, include_jv=False):
    if len(rows) != 4:
        return {k: None for k in ('cfo','leverage','capex','distribution','fcf','residual','roce')}
    def value(row, key):
        raw = row.get(key)
        if raw is None:
            return None
        result = Decimal(str(raw))
        return result if result.is_finite() else None
    cfo = ltm([value(r, 'cfo') for r in rows])
    capex = ltm([value(r, 'capex') for r in rows])
    if include_jv:
        contributions = ltm([value(r, 'jv_organic_contributions') for r in rows])
        capex = capex + contributions if capex is not None and contributions is not None else None
    distribution = ltm([value(r, 'distribution') for r in rows])
    ebitda = ltm([value(r, 'ebitda') for r in rows])
    debt = value(rows[-1], 'debt')
    lease = value(rows[-1], 'leases')
    if leases:
        debt = debt + lease if debt is not None and lease is not None else None
    def safe_ratio(a, b, factor=1):
        return ratio(a,b,factor) if a is not None and b is not None else None
    fcf = cfo-capex if cfo is not None and capex is not None else None
    residual = fcf-distribution if fcf is not None and distribution is not None else None
    return dict(cfo=cfo, leverage=safe_ratio(debt,ebitda), capex=safe_ratio(capex,cfo,100),
                distribution=safe_ratio(distribution,cfo,100), fcf=fcf, residual=residual,
                roce=roce(rows,leases,exclude_goodwill))
