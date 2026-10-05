from decimal import Decimal

def ratio(numerator, denominator, factor=1):
    return None if denominator == 0 else Decimal(str(numerator)) / Decimal(str(denominator)) * Decimal(str(factor))

def ltm(values):
    return None if len(values) != 4 or any(v is None for v in values) else sum(Decimal(str(v)) for v in values)

def quarter(ytd, previous_ytd=0):
    return Decimal(str(ytd)) - Decimal(str(previous_ytd))

def calculate(rows, leases=False):
    if len(rows) != 4:
        return {k: None for k in ('cfo','leverage','capex','distribution','fcf','residual','roce')}
    cfo = ltm([r['cfo'] for r in rows]); capex = ltm([r['capex'] for r in rows]); distribution = ltm([r['distribution'] for r in rows]); ebitda = ltm([r['ebitda'] for r in rows])
    debt = Decimal(str(rows[-1]['debt'])) + (Decimal(str(rows[-1]['leases'])) if leases else 0)
    return dict(cfo=cfo, leverage=ratio(debt, ebitda), capex=ratio(capex,cfo,100), distribution=ratio(distribution,cfo,100), fcf=cfo-capex, residual=cfo-capex-distribution, roce=None)
