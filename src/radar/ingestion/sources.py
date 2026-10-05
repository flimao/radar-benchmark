"""Bounded downloads from known public sources, with original bytes retained."""
import hashlib
import json
import os
import time
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

import httpx
from radar import data

HOSTS = {
    'Petrobras': ('petrobras.com.br', 'investidorpetrobras.com.br'),
    'TotalEnergies': ('totalenergies.com',),
    'Chevron': ('chevron.com', 'chevroncorp.gcs-web.com'),
    'Shell': ('shell.com',),
    'Bacen': ('olinda.bcb.gov.br', 'bcb.gov.br'),
    'Yahoo': ('query1.finance.yahoo.com', 'query2.finance.yahoo.com'),
}
MAX_BYTES = 20 * 1024 * 1024


def official(url, company):
    host = urlparse(url).hostname or ''
    # Petrobras' RI links to this tenant of its document hosting provider.
    if company == 'Petrobras' and host == 'api.mziq.com':
        return urlparse(url).scheme == 'https' and urlparse(url).path.startswith(
            '/mzfilemanager/v2/d/25fdf098-34f5-4608-b7fa-17d60b2de47d/')
    if host=='data.sec.gov' and company in data.COMPANIES:
        return urlparse(url).scheme=='https' and urlparse(url).path.startswith('/api/xbrl/companyfacts/CIK')
    return urlparse(url).scheme == 'https' and any(
        host == h or host.endswith('.' + h) for h in HOSTS.get(company, ()))


def permitted(url, company):
    parsed = urlparse(url)
    return (official(url, company) and not parsed.username and not parsed.password
            and parsed.port in (None, 443))


def download(url, company, *, client=None):
    if not permitted(url, company):
        raise ValueError('Download exige HTTPS em domínio autorizado da fonte/empresa.')
    owned = client is None
    client = client or httpx.Client(timeout=30, follow_redirects=False)
    user_agent='RADAR-PoC/0.1'
    if urlparse(url).hostname=='data.sec.gov':
        user_agent=os.environ.get('RADAR_SEC_USER_AGENT','')
        if not user_agent or '@' not in user_agent:
            if owned:client.close()
            raise ValueError('SEC exige RADAR_SEC_USER_AGENT com nome da aplicação e e-mail de contato.')
    try:
        # Validate each redirect, including scheme, host and port.
        for attempt in range(3):
            try:
                current = url
                for _ in range(6):
                    with client.stream('GET', current, headers={'User-Agent': user_agent}) as response:
                        if response.status_code in (301, 302, 303, 307, 308):
                            current = str(response.url.join(response.headers['location']))
                            if not permitted(current, company):
                                raise ValueError('Redirecionamento para fonte não autorizada.')
                            continue
                        response.raise_for_status()
                        payload = bytearray()
                        for chunk in response.iter_bytes():
                            payload.extend(chunk)
                            if len(payload) > MAX_BYTES:
                                raise ValueError('Download excede 20 MB.')
                        return bytes(payload), current
                raise ValueError('Redirecionamentos em excesso.')
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code not in (429, 500, 502, 503, 504):
                    raise
                if attempt == 2:
                    raise
                time.sleep(attempt + 1)
    finally:
        if owned:
            client.close()


def archive_api(payload, url, provider, scope):
    digest = hashlib.sha256(payload).hexdigest()
    directory = data.ROOT / 'data/original'
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / digest
    if not target.exists():
        target.write_bytes(payload)
    meta = {'hash': digest, 'url': url, 'provider': provider, 'scope': scope}
    return meta


def fetch_ptax(start, end, *, client=None):
    """One published closing sale quote per day; never intraday/holiday fill."""
    start, end = date.fromisoformat(start), date.fromisoformat(end)
    if end < start or (end-start).days > 366:
        raise ValueError('Consulta PTAX deve cobrir no máximo 366 dias.')
    url = str(httpx.URL(
        'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/'
        'CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)',
        params={'@moeda': "'USD'", '@dataInicial': start.strftime("'%m-%d-%Y'"),
                '@dataFinalCotacao': end.strftime("'%m-%d-%Y'"), '$format': 'json',
                '$top': '10000'}))
    payload, final = download(url, 'Bacen', client=client)
    # Bacen's OData implementation rejects tipoBoletim string filters; filter
    # the preserved complete response locally, retaining closing bulletins only.
    parsed = json.loads(payload, parse_float=Decimal)
    if parsed.get('@odata.nextLink') or parsed.get('odata.nextLink'):
        raise ValueError('Resposta PTAX paginada; reduza o intervalo.')
    rates = {}; duplicate_rows=0
    for row in parsed['value']:
        if row['tipoBoletim'] != 'Fechamento':
            continue
        day = row['dataHoraCotacao'][:10]
        rate = Decimal(str(row['cotacaoVenda']))
        if not start <= date.fromisoformat(day) <= end or not rate.is_finite() or rate <= 0:
            raise ValueError('PTAX inválida, duplicada ou fora do intervalo solicitado.')
        if day in rates:
            if Decimal(rates[day])!=rate:
                raise ValueError('PTAX duplicada com cotações conflitantes no mesmo dia.')
            duplicate_rows+=1
            continue
        rates[day] = str(rate)
    if not rates:
        raise ValueError('Bacen não retornou cotações de fechamento.')
    return {'rates': rates, 'identical_closing_duplicates_removed':duplicate_rows, 'start': start.isoformat(), 'end': end.isoformat(),
            **archive_api(payload, final, 'Bacen', f'{start}/{end}')}


def fetch_yahoo(symbol, start, end, *, client=None):
    """Optional market context, not statutory financial facts or accounting FX."""
    from datetime import datetime, timezone
    from urllib.parse import quote
    start_date, end_date = date.fromisoformat(start), date.fromisoformat(end)
    if end_date < start_date or (end_date-start_date).days > 3660:
        raise ValueError('Intervalo Yahoo inválido (máximo 10 anos).')
    if symbol not in ('BZ=F', 'BRL=X', 'CVX', 'SHEL', 'TTE', 'PBR'):
        raise ValueError('Símbolo de contexto não autorizado.')
    timestamp = lambda d: int(datetime.combine(d, datetime.min.time(), timezone.utc).timestamp())
    url = str(httpx.URL('https://query1.finance.yahoo.com/v8/finance/chart/' + quote(symbol, safe=''),
                        params={'period1': timestamp(start_date), 'period2': timestamp(end_date+timedelta(days=1)),
                                'interval': '1d'}))
    payload, final = download(url, 'Yahoo', client=client)
    parsed = json.loads(payload, parse_float=Decimal)
    if parsed['chart'].get('error') or not parsed['chart'].get('result'):
        raise ValueError('Série Yahoo indisponível.')
    result = parsed['chart']['result'][0]
    timestamps = result.get('timestamp', [])
    closes = result['indicators']['quote'][0].get('close', [])
    if len(timestamps) != len(closes):
        raise ValueError('Série Yahoo inconsistente.')
    zone = result['meta'].get('exchangeTimezoneName', 'UTC')
    from zoneinfo import ZoneInfo
    points = []
    for stamp, close in zip(timestamps, closes):
        if close is None:
            continue
        day = datetime.fromtimestamp(stamp, ZoneInfo(zone)).date()
        value = Decimal(str(close))
        if not value.is_finite():
            raise ValueError('Preço Yahoo inválido.')
        if start_date <= day <= end_date:
            points.append({'date': str(day), 'close': str(value)})
    if not points or len({p['date'] for p in points}) != len(points):
        raise ValueError('Série Yahoo vazia ou duplicada.')
    return {'symbol': symbol, 'currency': result['meta'].get('currency'), 'points': points,
            'usage': 'CONTEXTO', 'note': 'Yahoo Finance; futuro contínuo BZ=F não equivale ao Brent físico. BRL=X não substitui PTAX.',
            **archive_api(payload, final, 'Yahoo', f'{symbol}:{start}/{end}')}


def fetch_sec_companyfacts(company, cik, *, client=None):
    """Financial XBRL API; preserve filing/accession context for explicit mapping."""
    if company not in data.COMPANIES or not str(cik).isdigit() or len(str(cik))>10:
        raise ValueError('Empresa/CIK inválido.')
    data.initialize()
    url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json'
    payload,final=download(url,company,client=client)
    parsed=json.loads(payload)
    if int(parsed['cik'])!=int(cik) or not parsed.get('facts'):
        raise ValueError('Resposta SEC sem fatos ou de outro emissor.')
    result=archive_api(payload,final,'SEC',company+':'+str(cik))
    digest,_=data.preserve(payload,company+'-companyfacts.json',company,'MULTIPERIOD',final,'XBRL CompanyFacts CIK '+str(cik))
    return {**result,'company':company,'cik':str(cik),'entity_name':parsed['entityName'],
            'note':'Mapear namespace, tag, unidade, datas e accession; duplicidades de filing exigem seleção explícita.'}
