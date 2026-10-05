# RADAR — benchmarking de óleo e gás

Aplicação local Python/Flask/Dash criada a partir do DRS v2.0. Interface em português para Petrobras, TotalEnergies, Chevron e Shell, sem ranking composto e sem uso de logomarcas corporativas.

## Executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
python -m radar.web.app
```

Abra http://127.0.0.1:8050. Sem credenciais, a execução local utiliza modo de demonstração explícito. Os números são **sintéticos**, não resultados financeiros reais. Eles nunca devem ser usados em análise financeira. O servidor de desenvolvimento escuta somente localhost.

## Recursos disponíveis

- Nove páginas: resumo, trajetória, comparação, drivers, ponte de caixa, qualidade, metodologia, regras e carga.
- Filtros de empresas, período, visão e sensibilidade de leases.
- Cálculos decimais de FCO LTM, dívida líquida/EBITDA, CAPEX/FCO, distribuições/FCO, FCL e caixa residual.
- Hierarquia de imposto operacional aprovada (OPEN-03); ROCE calculado no cenário sintético com alíquotas fictícias específicas por empresa; dados reais pendentes; visão reportada sintética separada.
- DuckDB com chave empresa/período/versão e valores DECIMAL(28,6).
- Upload de originais com SHA-256, idempotência, tamanho limitado, URL/locator e histórico de revisão. Arquivos nunca são executados nem publicados automaticamente como fatos.
- Exportação CSV/Parquet do mesmo dataset tabular, para uso local no Power BI.
- Senha compartilhada opcional no modo local, obrigatória em produção; CSRF no login, limitação de tentativas e rotas protegidas.

## Acesso com senha

Gere um hash (digite a senha sem gravá-la no histórico):

```bash
python -c 'from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass()))'
python -c 'import secrets; print(secrets.token_hex(32))'
```

Defina `RADAR_PASSWORD_HASH` com o primeiro resultado e `RADAR_SESSION_SECRET` com o segundo. Para HTTP local deixe `RADAR_HTTPS=0`; em HTTPS defina `1`. Não há senha padrão.

## Testes

```bash
pytest -q
```

## Container / VPS

Configuração aprovada: **2 vCPUs, 4 GB RAM e 80 GB SSD**, Ubuntu Server última LTS.

```bash
.venv/bin/python scripts/configure_container.py
docker compose -f compose.test.yaml build
docker compose -f compose.test.yaml run --rm tests
docker compose up --build -d --wait
```

Abra http://127.0.0.1:8051/login. O container usa seu próprio volume persistente e requer senha. Para macOS com Docker Desktop fora do PATH, e para HTTPS/VPS, consulte [runbook do container](docs/container-runbook.md).

## Estado do DRS

Esta entrega é uma base funcional demonstrativa, **não o aceite integral da PoC financeira**. Consulte [docs/estado-do-drs.md](docs/estado-do-drs.md) para pendências. O arquivo `.pbix` exige Power BI Desktop e ainda não foi criado; há tema e dataset exportável. Não há coleta/extrator automático homologado nem quatro trimestres reais aprovados.
