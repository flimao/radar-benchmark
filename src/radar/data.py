import hashlib, json, os
from decimal import Decimal
from pathlib import Path
import duckdb
import pandas as pd
from radar.domain import calculate
ROOT = Path(os.environ.get('RADAR_DATA_DIR', '.'))
COMPANIES = {'Petrobras':('#008542','IFRS','Brasil'), 'Equinor':('#008e91','IFRS','Noruega'), 'Chevron':('#006298','US GAAP','Estados Unidos'), 'Shell':('#b28700','IFRS','Reino Unido')}
SOURCES = {'Petrobras':'https://www.investidorpetrobras.com.br/resultados-e-comunicados/central-de-resultados/', 'Equinor':'https://www.equinor.com/investors/quarterly-results', 'Chevron':'https://www.chevron.com/investors', 'Shell':'https://www.shell.com/investors/results-and-reporting/quarterly-results.html'}
RULES = json.loads((Path(os.environ.get('RADAR_PROJECT_DIR', '.'))/'config/rules.json').read_text())
ROCE_FIELDS = ['ebit_adjusted','operating_tax','tax_rate','capital_employed_open','capital_employed_close','leases_open']
PERIODS=['2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4']

def demo_rows():
    rows=[]
    bases={'Petrobras':(8900,3000,4300,16500,11200), 'Equinor':(6000,2700,3000,7300,9400), 'Chevron':(8200,4100,4900,21900,10300), 'Shell':(11200,5100,6100,33700,14600)}
    for company, base in bases.items():
        for i,p in enumerate(PERIODS):
            f=[1.04,0.94,1.10,1.03,0.96,1.06,1.02,1.12][i]
            cfo,capex,dist,debt,ebitda=base
            rows.append(dict(company=company,period=p,cfo=round(cfo*f),capex=round(capex*(0.95+i*.018)),distribution=round(dist*(1.02-i*.012)),debt=round(debt*(1.03-i*.008)),ebitda=round(ebitda*f),leases=round(debt*.18),roce=round(12+list(bases).index(company)*1.2+i*.3,1),version=1,mode='DEMONSTRACAO'))
    for row in rows:
        i = PERIODS.index(row['period'])
        base = bases[row['company']]
        # Explicit demo balances: synthetic net debt + synthetic equity/NCI.
        equity_nci_base = Decimal(str(base[0])) * 8
        net_debt_base = Decimal(str(base[3]))
        def capital_at(boundary):
            equity_nci = equity_nci_base * (1 + Decimal(boundary) * Decimal('.012'))
            net_debt = net_debt_base * (Decimal('1.03') - Decimal(boundary) * Decimal('.008'))
            return equity_nci + net_debt
        row['ebit_adjusted'] = Decimal(str(row['ebitda'])) * Decimal(str(RULES['synthetic_roce']['ebit_fraction_of_ebitda']))
        row['tax_rate'] = Decimal(str(RULES['synthetic_roce']['tax_rates'][row['company']]))
        row['operating_tax'] = row['ebit_adjusted'] * row['tax_rate']
        row['capital_employed_open'] = capital_at(i - 1)
        row['capital_employed_close'] = capital_at(i)
        row['leases_open'] = Decimal(str(row['leases']))
    return rows

def initialize():
    for p in ['database','data/original','data/curated','evidence']: (ROOT/p).mkdir(parents=True,exist_ok=True)
    with duckdb.connect(str(ROOT/'database/radar.duckdb')) as db:
        db.execute('CREATE TABLE IF NOT EXISTS facts(company VARCHAR, period VARCHAR, cfo DECIMAL(28,6), capex DECIMAL(28,6), distribution DECIMAL(28,6), debt DECIMAL(28,6), ebitda DECIMAL(28,6), leases DECIMAL(28,6), roce DECIMAL(28,6), version INTEGER, mode VARCHAR, PRIMARY KEY(company,period,version))')
        db.execute('CREATE TABLE IF NOT EXISTS documents(hash VARCHAR PRIMARY KEY, filename VARCHAR, company VARCHAR, period VARCHAR, source_url VARCHAR, locator VARCHAR, status VARCHAR, created_at TIMESTAMP DEFAULT current_timestamp)')
        columns = {r[1] for r in db.execute("PRAGMA table_info('facts')").fetchall()}
        for name in ROCE_FIELDS:
            if name not in columns:
                db.execute(f'ALTER TABLE facts ADD COLUMN {name} DECIMAL(28,6)')
        seed = pd.DataFrame(demo_rows())
        db.register('seed', seed)
        if not db.execute('SELECT count(*) FROM facts').fetchone()[0]:
            names = ','.join(seed.columns)
            db.execute(f'INSERT INTO facts ({names}) SELECT {names} FROM seed')
        else:
            # Add a demo revision, preserving original version 1 and all real records.
            fields = ','.join(ROCE_FIELDS)
            db.execute(f"""INSERT INTO facts
                SELECT f.company,f.period,f.cfo,f.capex,f.distribution,f.debt,f.ebitda,
                       f.leases,f.roce,f.version+1,f.mode,{','.join('s.'+k for k in ROCE_FIELDS)}
                FROM facts f JOIN seed s ON f.company=s.company AND f.period=s.period
                WHERE f.mode='DEMONSTRACAO' AND f.ebit_adjusted IS NULL
                  AND f.version=(SELECT max(f2.version) FROM facts f2 WHERE f2.company=f.company AND f2.period=f.period)
                """)

def facts():
    with duckdb.connect(str(ROOT/'database/radar.duckdb'),read_only=True) as db:
        return db.execute('SELECT * FROM facts ORDER BY company,period,version').df()

def metrics(period, selected, leases=False):
    df=facts(); result=[]
    periods=sorted(df.period.unique()); end=periods.index(period)
    for company in selected:
        rows=df[(df.company==company)&(df.period.isin(periods[max(0,end-3):end+1]))].sort_values(['period','version']).drop_duplicates('period',keep='last').to_dict('records')
        values=calculate(rows,leases)
        result.append(dict(company=company,**{k:float(v) if v is not None else None for k,v in values.items()},reported_roce=float(rows[-1]['roce']) if rows else None))
    return result

def preserve(content, filename, company, period, url, locator):
    digest=hashlib.sha256(content).hexdigest(); target=ROOT/'data/original'/digest
    if not target.exists(): target.write_bytes(content)
    with duckdb.connect(str(ROOT/'database/radar.duckdb')) as db:
        exists=db.execute('SELECT hash FROM documents WHERE hash=?',[digest]).fetchone()
        if exists: return digest,'NO_CHANGE'
        db.execute('INSERT INTO documents(hash,filename,company,period,source_url,locator,status) VALUES (?,?,?,?,?,?,?)',[digest,filename,company,period,url,locator,'REVISAO'])
    return digest,'REVISAO'

def documents():
    with duckdb.connect(str(ROOT/'database/radar.duckdb'),read_only=True) as db: return db.execute('SELECT * FROM documents ORDER BY created_at DESC').df()

def export():
    frame=facts(); frame.to_parquet(ROOT/'data/curated/facts.parquet',index=False); frame.to_csv(ROOT/'data/curated/facts.csv',index=False)
    return frame
