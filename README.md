# RADAR — benchmarking de óleo e gás

Aplicação Python/Flask/Dash para comparar Petrobras, TotalEnergies, Chevron e Shell. Interface em português, com indicadores financeiros, trajetória histórica, drivers operacionais e rastreabilidade das fontes. Não utiliza ranking composto nem logomarcas corporativas.

Produção: [radar-benchmark.felipeloliveira.com.br](https://radar-benchmark.felipeloliveira.com.br), com autenticação. Release publicada: **v2.4**.

## Funcionalidades

- **Resumo executivo:** geração e alocação de caixa e indicadores das empresas lado a lado.
- **Posição e trajetória:** histórico de ROCE/ROACE, FCO, dívida líquida/EBITDA, CAPEX/FCO e distribuições/FCO. O eixo temporal mostra períodos com indicadores calculados.
- **Comparação por KPI:** comparação entre empresas no mesmo trimestre de referência, mantendo a base LTM.
- **Ponte de caixa:** FCO, CAPEX orgânico, caixa livre, distribuições e caixa residual.
- **Drivers e contexto:** Brent futuro, PTAX Bacen, mix trimestral de líquidos/gás, margem indicativa de refino com preços spot da EIA e Brent de equilíbrio de caixa estimado, orgânico e após distribuições. As séries temporais permitem sobrepor um KPI no segundo eixo.
- **Filtros:** base real ou demonstração, empresas, trimestre, visão padronizada ou ROCE reportado; sensibilidades de leases, goodwill e aportes orgânicos em JVs.
- **Qualidade, metodologia e regras:** fórmulas, fontes, revisões e justificativas de comparabilidade. Valores ausentes permanecem indisponíveis; alternativas documentadas mantêm ressalvas em pictogramas, losangos e hachuras.
- **Administração de carga (`/admin`):** períodos, documentos preservados, conciliação, revisão e publicação de lotes. Links permitem baixar os originais armazenados. Os controles de envio de documentos e mapeamento JSON estão desativados na interface, com indicação de bloqueio pela SI Petrobras; a lógica de ingestão permanece no projeto.
- **Exportação:** CSV e Parquet; banco DuckDB com valores decimais e versões; documentos originais identificados por SHA-256.

A margem de refino é um benchmark comum de mercado, não a margem realizada de cada empresa. O Brent de equilíbrio é um cenário com sensibilidade de US$ 1 de caixa por barril de líquidos para cada US$ 1/b de variação do Brent, não um breakeven econômico efetivo. Consulte a metodologia na interface.

## Instalar e executar com Python

Requisitos: **Python 3.12 ou superior**, Git e terminal. Execute os comandos a partir da raiz do repositório: a aplicação lê `config/` nesse diretório.

```bash
git clone gh:flimao/radar-benchmark.git
cd radar-benchmark
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -c constraints.txt -r requirements.txt
python -m pip install --no-deps -e .
python -m radar.web.app
```

O endereço SSH acima requer o alias `gh` configurado na sua máquina. Sem esse alias, use `git@github.com:flimao/radar-benchmark.git`.

Abra [http://127.0.0.1:8050](http://127.0.0.1:8050). O servidor local escuta somente localhost. Sem `RADAR_PASSWORD_HASH`, não exige login. Para outra porta e um diretório persistente de dados separado:

```bash
RADAR_DATA_DIR="$PWD/runtime-data" PORT=8052 python -m radar.web.app
```

O banco e as pastas de dados são criados automaticamente. Para reiniciar após mudanças de código ou dos snapshots em `config/`, interrompa com **Ctrl+C** e execute novamente o comando. Este servidor não usa recarga automática.

### Bases de dados

Uma instalação nova inicializa a base **Demonstração**, com números sintéticos. Eles não são resultados financeiros reais. Os fatos financeiros reais publicados no ambiente de produção **não são distribuídos pelo clone do Git**: exigem uma base persistente com lotes ingeridos e publicados, ou uma restauração de backup autorizado.

Selecione **Reais · aprovados** para consultar somente fatos financeiros publicados. A versão atual de produção tem dados de 2024–2025 das quatro empresas, com alternativas e limitações documentadas. Isso não significa equivalência metodológica integral entre todos os indicadores.

Os snapshots operacionais do mix de produção e dos preços EIA de 2024–2025 estão versionados em `config/production-mix.json` e `config/refining-market.json`. As séries coletadas de PTAX e Brent futuro dependem do diretório de dados. Dados faltantes não são substituídos automaticamente pela demonstração.

### Variáveis de ambiente

| Variável | Uso |
|---|---|
| `PORT` | Porta do servidor Python local; padrão `8050` |
| `RADAR_PROJECT_DIR` | Raiz contendo `config/`; padrão: diretório atual |
| `RADAR_DATA_DIR` | Raiz de banco, originais e evidências; padrão: diretório atual |
| `RADAR_PASSWORD_HASH` | Hash Werkzeug da senha compartilhada |
| `RADAR_SESSION_SECRET` | Segredo de sessão; obrigatório quando há senha |
| `RADAR_HTTPS` | `0` para HTTP local; `1` para cookies seguros sob HTTPS |
| `RADAR_ENV` | `production` exige senha configurada |
| `RADAR_PORT` | Porta externa do Docker Compose; padrão `8051` |
| `RADAR_SEC_USER_AGENT` | Identificação para acesso às fontes SEC; veja `.env.example` |

Não há senha padrão. Para gerar hash e segredo, sem registrar a senha no histórico:

```bash
python -c 'from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass()))'
python -c 'import secrets; print(secrets.token_hex(32))'
```

Exporte os resultados como `RADAR_PASSWORD_HASH` e `RADAR_SESSION_SECRET` antes de iniciar o servidor local. Preserve os `$` do hash usando aspas simples. O comando Python local não carrega `.env` automaticamente; o Docker Compose o carrega.

## Executar com Docker

Requisitos: Docker Engine/Desktop em execução e Docker Compose v2. Após instalar o ambiente Python acima:

```bash
python scripts/configure_container.py
docker compose up --build -d --wait
```

O script solicita e confirma a senha, cria `.env` com hash e segredo e não sobrescreve um arquivo existente. Abra [http://127.0.0.1:8051/login](http://127.0.0.1:8051/login). Para alterar a porta, ajuste `RADAR_PORT` no `.env`.

```bash
docker compose logs --tail=100 radar
docker compose restart radar
```

Após alterações de código ou configuração versionada, reconstrua com `docker compose up --build -d --wait`. O container usa Gunicorn e um volume persistente próprio, separado da execução Python local. `docker compose down` preserva o volume; **`docker compose down -v` apaga o volume e seus dados**.

Para VPS, configure `RADAR_HTTPS=1` no `.env` e um proxy HTTPS, como Caddy, encaminhando para `127.0.0.1:8051`. Faça backup consistente do banco e dos documentos antes de atualizações. Consulte o [runbook do container e VPS](docs/container-runbook.md) para detalhes operacionais e registros históricos de implantação.

## Testes

No ambiente Python:

```bash
python -m pip install -c constraints.txt 'pytest>=8'
pytest -q
```

Ou com Docker:

```bash
docker compose -f compose.test.yaml build
docker compose -f compose.test.yaml run --rm tests
```

## Ingestão e documentação

A pipeline prepara lotes financeiros rastreáveis para revisão e publicação; carregar um documento não publica fatos automaticamente. A ingestão continua disponível no código, mesmo com os controles de arquivos desativados na interface.

- [Pipeline de ingestão](docs/pipeline-ingestao.md) e exemplos em `config/ingestion/`.
- [Mix de produção 2024–2025](docs/mix-producao-2024-2025.md).
- [Benchmark comum de refino](docs/margem-refino-benchmark.md).
- [Estado do DRS](docs/estado-do-drs.md): registro de requisitos e pendências; consulte suas datas, pois partes descrevem etapas anteriores do projeto.

Para atualizar o snapshot de preços EIA:

```bash
RADAR_DATA_DIR="$PWD/runtime-data" python -m radar.ingestion.refining --start 2024-01-01 --end 2025-12-31
```

O coletor valida as três fontes antes de substituir o snapshot e preserva os originais HTML no diretório de dados. Mudanças no snapshot exigem reinício local ou reconstrução da imagem Docker.
