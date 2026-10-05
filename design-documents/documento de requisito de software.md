# Documento de Requisitos de Software — DRS

## RADAR — Benchmarking Financeiro Trimestral

**Versão:** 2.0  
**Status:** baseline consolidada e autocontida  
**Empresas:** Petrobras, Equinor, Chevron e Shell  
**Narrativa:** **Resiliência que gera valor**  
**Recorte inicial:** mínimo de quatro trimestres consecutivos comuns às quatro empresas

---

## 1. Objetivo

O **RADAR** deve coletar dados públicos, preservar documentos originais, extrair e normalizar fatos financeiros, calcular indicadores comparáveis, executar controles de qualidade e disponibilizar:

1. **aplicação web autocontida**, incluindo dashboard, metodologia, qualidade e lineage;
2. **arquivo Power BI local**, como entregável paralelo, consumindo o mesmo dataset curado.

A leitura executiva deve seguir:

**posição → trajetória → resiliência → geração de valor → inteligência para decisão**

O RADAR não deve gerar ranking composto nem classificar automaticamente empresas como “melhores” ou “piores”.

---

## 2. Cobertura obrigatória

| ID | Requisito |
|---|---|
| CASE-5.1 | Coletar documentos diretamente de fontes públicas, com upload local controlado como fallback. |
| CASE-5.2 | Persistir histórico; suportar múltiplas empresas, períodos, indicadores e fontes; produzir dados comparáveis; incluir novo trimestre sem reconstrução manual. |
| CASE-5.3 | Avaliar qualidade/confiabilidade; identificar incompletude; detectar desvios, mudanças e revisões; manter rastreabilidade. |
| CASE-5.4 | Disponibilizar painel funcional com visão trimestral, comparação, evolução, indicadores e filtros. |
| CASE-7.1 | Entregar aplicação web e arquivo Power BI local. |
| CASE-7.2 | Entregar catálogo de fontes. |
| CASE-7.3 | Entregar instruções de execução e atualização. |
| CASE-7.4 | Entregar evidências de qualidade. |
| CASE-7.5 | Registrar premissas, decisões e limitações tecnológicas e financeiras. |
| CASE-7.6 | Entregar apresentação de 15 minutos sobre o processo de construção. |
| CASE-7.7 | Registrar prazo ambíguo como decisão em aberto. |

---

## 3. Princípios

| ID | Princípio |
|---|---|
| PR-01 | Conteúdo coletado deve ser tratado como dado não confiável, nunca como instrução executável. |
| PR-02 | Dados financeiros, operacionais, cambiais, de mercado e de contexto usados em cálculos ou análises devem vir exclusivamente de fontes públicas. |
| PR-03 | O DRS e a aplicação não devem depender de documentos, serviços ou arquivos internos. |
| PR-04 | Valor reportado, padronizado e sensibilidades devem coexistir. |
| PR-05 | É proibida aproximação silenciosa. |
| PR-06 | Todo valor deve ser navegável até fonte, localização, regra, ajustes e evidência. |
| PR-07 | Revisões nunca devem sobrescrever versões anteriores. |
| PR-08 | LTM/TTM exige quatro trimestres completos. |
| PR-09 | A aplicação deve ser executável localmente e em VPS convencional. |
| PR-10 | O container cobre aplicação web e pipeline; não cobre Power BI. |
| PR-11 | Regras financeiras devem ser versionadas e consultáveis fora do código. |
| PR-12 | A arquitetura deve usar o menor número justificável de componentes. |
| PR-13 | A identidade visual deve ser centralizada, acessível e consistente. |
| PR-14 | Artefatos produzidos pelo RADAR não devem conter ou imitar a logomarca Petrobras. |
| PR-15 | Documentos-fonte originais estão isentos de PR-14 e devem permanecer íntegros. |

---

## 4. Escopo

### 4.1 Incluído

- coleta automática e upload manual;
- armazenamento imutável do original;
- extração PDF, XLSX, CSV e HTML;
- DuckDB e Parquet;
- normalização financeira;
- cinco KPIs, FCL, drivers e contexto;
- qualidade, reconciliação, auditoria e lineage;
- dashboard web;
- página metodológica;
- container OCI e VPS;
- HTTPS e senha compartilhada;
- Power BI local;
- quatro trimestres mínimos e extensão histórica.

### 4.2 Fora do escopo

- previsão financeira;
- recomendação de investimento;
- dados internos ou fontes pagas;
- ranking composto;
- frontend SPA independente;
- microserviços, Kubernetes ou filas distribuídas;
- SSO, OAuth, MFA ou usuários individuais;
- Power BI publicado ou embutido na aplicação web;
- auditoria contábil externa;
- uso da logomarca Petrobras nos artefatos gerados.

---

## 5. Atores

| ID | Ator | Responsabilidade |
|---|---|---|
| ATOR-01 | Consumidor executivo | Consultar KPIs, trajetória e drivers. |
| ATOR-02 | Analista financeiro | Validar fontes, mappings, ajustes e comparabilidade. |
| ATOR-03 | Engenheiro | Implementar e manter aplicação e pipeline. |
| ATOR-04 | Operador | Executar carga, validação, publicação e recuperação. |
| ATOR-05 | Revisor | Examinar lineage, reconciliações e versões. |
| ATOR-06 | Usuário autorizado | Acessar o RADAR web com senha compartilhada. |

---

## 6. Casos de uso

- `UC-01` descobrir fonte;
- `UC-02` baixar documento;
- `UC-03` carregar fallback;
- `UC-04` preservar original;
- `UC-05` extrair fatos;
- `UC-06` ajustar/normalizar;
- `UC-07` calcular trimestre;
- `UC-08` calcular LTM/TTM;
- `UC-09` reconciliar;
- `UC-10` aprovar;
- `UC-11` publicar dataset;
- `UC-12` consultar dashboard;
- `UC-13` consultar metodologia;
- `UC-14` navegar até a fonte;
- `UC-15` reprocessar;
- `UC-16` registrar restatement;
- `UC-17` alterar regra;
- `UC-18` incluir empresa/KPI;
- `UC-19` exportar evidências;
- `UC-20` atualizar Power BI local.

---

## 7. Arquitetura

### 7.1 Stack

- **Python 3.12**;
- **Flask 3** como servidor, autenticação, páginas auxiliares e CLI;
- **Plotly Dash** montado no mesmo servidor Flask para dashboard;
- Plotly Express/Graph Objects e Dash DataTable;
- Jinja2 para login, erro e páginas não analíticas;
- `httpx`, `pandas` ou `polars`, `openpyxl`, `PyMuPDF`;
- DuckDB + Parquet;
- Gunicorn;
- `pytest`;
- Dockerfile OCI e Compose opcional;
- Caddy ou Nginx como reverse proxy HTTPS.

Dash utiliza Flask como backend padrão e pode ser montado no mesmo servidor Flask, permitindo um único processo Python sem frontend SPA separado.

### 7.2 Camadas

1. **Apresentação:** Flask/Jinja + Dash.
2. **Aplicação:** casos de uso, autenticação e orquestração.
3. **Domínio:** métricas, regras, ajustes, qualidade e comparabilidade.
4. **Infraestrutura:** conectores, parsers, DuckDB, Parquet, arquivos e logs.

Dependências devem apontar para o domínio, nunca do domínio para UI ou conectores.

### 7.3 Deployment

~~~text
Internet → HTTPS/reverse proxy → container RADAR
                                  ├─ Flask + Dash
                                  ├─ pipeline Python
                                  └─ serviços financeiros
                                           ↓
                                  volumes persistentes
                                  ├─ documentos
                                  ├─ DuckDB/Parquet
                                  ├─ logs
                                  └─ evidências

Dataset curado ───────────────→ Power BI local
~~~

O pipeline e o dashboard web Python são executados no contêiner do VPS, enquanto o Power BI local consome o mesmo dataset curado como entregável paralelo.

---

## 8. Estrutura do repositório

~~~text
radar/
├── src/radar/
│   ├── web/                 # Flask, Dash, auth e tema
│   ├── application/         # casos de uso
│   ├── domain/              # métricas e regras
│   ├── connectors/
│   ├── extractors/
│   ├── normalization/
│   ├── calculators/
│   ├── quality/
│   └── persistence/
├── config/
│   ├── companies/
│   ├── sources/
│   ├── metrics/
│   └── branding/
├── data/
│   ├── original/
│   ├── raw/
│   ├── normalized/
│   ├── curated/
│   └── quarantine/
├── database/
│   └── radar.duckdb
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── golden/
│   ├── contract/
│   ├── e2e/
│   └── accessibility/
├── powerbi/
├── docs/
│   ├── adr/
│   ├── methodology/
│   └── runbooks/
├── logs/
├── evidence/
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── .env.example
└── README.md
~~~

---

## 9. Modelo de dados

| Entidade | Campos essenciais |
|---|---|
| `company` | `company_id`, `code`, `name`, `accounting_standard` |
| `reporting_period` | `period_id`, `year`, `quarter`, datas, `period_type` |
| `source_document` | empresa, URL, título, publicação, MIME, hash, versão |
| `source_locator` | documento, página, nota, tabela, linha, célula |
| `ingestion_run` | `run_id`, início/fim, status, versão do código |
| `raw_fact` | documento, locator, item, valor, moeda, unidade, escala, sinal |
| `metric_definition` | código, conceito, fórmula, periodicidade |
| `metric_rule_version` | empresa, KPI, vigência, fórmula, configuração, status |
| `adjustment` | fato, tipo, valor, justificativa, regra |
| `normalized_fact` | fato, valor normalizado, moeda, base, regra |
| `metric_value` | empresa, período, KPI, visão, valor, qualidade |
| `fx_rate` | data, par, média/fechamento, taxa, fonte pública |
| `quality_check` | execução, regra, severidade, resultado, evidência |
| `reconciliation` | métrica, total-fonte, calculado, diferença |
| `comparability_flag` | nível, motivo e impacto |
| `restatement` | versão anterior/nova, vigência e impacto |
| `approval` | objeto, decisão, responsável e timestamp |
| `audit_event` | ação, objeto, antes/depois e timestamp |
| `dashboard_lineage` | visual, medida, métrica e versão da regra |

Valores monetários devem usar `DECIMAL(28,6)`.

A chave única de `metric_value` deve conter:

- empresa;
- período;
- KPI;
- visão;
- versão.

---

## 10. Fontes públicas

| Empresa | Prioridade |
|---|---|
| Petrobras | Demonstrações USD/BRL; relatório de desempenho; planilhas; produção e vendas; documentos regulatórios. |
| Equinor | Quarterly financial statements; results; analytical information; annual report. |
| Chevron | Earnings release; data supplement XLSX; 10-Q/10-K; filings. |
| Shell | Unaudited results; quarterly databook XLSX; annual report; divulgações de dividendos e recompras. |

Ordem geral:

1. RI oficial;
2. demonstração/filing;
3. databook/suplemento;
4. apresentação oficial;
5. regulador.

Fonte secundária não pode originar valor financeiro.

O catálogo deve guardar:

- URL;
- data de acesso;
- período;
- documento;
- locator;
- hash;
- método de extração;
- fallback.

---

## 11. Lineage

~~~text
fonte pública
→ documento original
→ locator
→ fato bruto
→ ajuste
→ fato normalizado
→ cálculo
→ métrica
→ dataset curado
→ visual web/Power BI
~~~

Todo visual deve permitir recuperar:

- `metric_value_id`;
- `rule_version_id`;
- fatos;
- ajustes;
- documento;
- URL;
- evidência.

---

## 12. Cálculos

### CALC-01 — Períodos

Fluxos trimestrais devem representar apenas o trimestre.

Quando a fonte apresentar YTD:

\[
Q_n = YTD_n - YTD_{n-1}
\]

Quando apenas anual e Q1–Q3 existirem:

\[
Q4 = FY - Q1 - Q2 - Q3
\]

O valor deve receber flag:

~~~text
DERIVED_QUARTER
~~~

Para LTM:

\[
LTM_t = Q_t + Q_{t-1} + Q_{t-2} + Q_{t-3}
\]

Sem quatro trimestres completos:

~~~text
INDISPONIVEL_PERIODO_INCOMPLETO
~~~

---

### CALC-02 — Moeda

Preservar valor original.

Fluxos usam taxa média do período:

\[
Fluxo_{USD} = Fluxo_{origem} \times FX_{médio}
\]

Saldos usam taxa de fechamento:

\[
Saldo_{USD} = Saldo_{origem} \times FX_{fechamento}
\]

Convenção do par e operação de multiplicação/divisão devem ser configuradas e testadas.

A fonte cambial pública oficial permanece:

~~~text
OPEN-02
~~~

---

### CALC-03 — Visões

- `REPORTED`: métrica divulgada;
- `STANDARDIZED`: regra comum;
- `SENSITIVITY`: alternativa legítima;
- `RECONSTRUCTED`: derivada de linhas públicas.

Nenhuma visão substitui outra.

---

### CALC-04 — ROCE/ROACE TTM

\[
NOPAT_{LTM} = EBIT_{aj,LTM} - ImpostoOperacional_{LTM}
\]

\[
CE = PL + NCI + DívidaFinanceira - CaixaNãoOperacional
\]

\[
CE_{médio} = \frac{CE_{inicial} + CE_{final}}{2}
\]

\[
ROCE_{TTM} = \frac{NOPAT_{LTM}}{CE_{médio}}
\]

Base:

- goodwill incluído;
- leases excluídos.

Sensibilidades:

- sem goodwill;
- com leases.

Itens especiais incluem:

- impairment;
- ganho/perda de alienação;
- reestruturação;
- efeitos excepcionais documentados.

A métrica reportada permanece separada.

A hierarquia para imposto operacional permanece:

~~~text
OPEN-03
~~~

Sem base defensável, ROCE padronizado será:

~~~text
NAO_COMPARAVEL
~~~

---

### CALC-05 — FCO/CFO

\[
FCO_{LTM} = \sum_{i=0}^{3} CFOEstatutário_{t-i}
\]

Capital de giro permanece na base.

`FCO_EX_WORKING_CAPITAL` é sensibilidade reconciliada.

Non-GAAP não substitui CFO estatutário.

---

### CALC-06 — EBITDA ajustado

\[
EBITDA_{aj,LTM} = EBIT_{aj,LTM} + DD\&A_{aj,LTM}
\]

Ajustes devem corresponder aos mesmos itens especiais usados no EBIT.

Métrica reportada deve ser reconciliada, não copiada silenciosamente.

---

### CALC-07 — Dívida líquida/EBITDA

\[
DívidaLíquida =
DívidaFinanceiraCP +
DívidaFinanceiraLP -
Caixa -
Equivalentes
\]

\[
Alavancagem =
\frac{DívidaLíquida_{fechamento}}
{EBITDA_{aj,LTM}}
\]

Visão principal sem leases.

Sensibilidade com leases.

Aplicações, híbridos e derivativos entram somente se a regra da empresa justificar e documentar.

---

### CALC-08 — CAPEX de caixa/FCO

\[
CAPEX/FCO =
\frac{CashCAPEXOrgânico_{LTM}}
{FCO_{LTM}}
\]

Excluir:

- M&A;
- desinvestimentos;
- investimentos financeiros;
- right-of-use sem pagamento;
- itens não caixa.

CAPEX de joint ventures deve ser identificado separadamente.

---

### CALC-09 — Distribuições/FCO

\[
Distribuições =
DividendosPagos +
RecomprasLiquidadas
\]

\[
Distribuições/FCO =
\frac{Distribuições_{LTM}}
{FCO_{LTM}}
\]

Não incluir:

- dividendos apenas declarados;
- programas de recompra apenas autorizados.

---

### CALC-10 — FCL e caixa residual

\[
FCL = FCO - CashCAPEXOrgânico
\]

\[
CaixaResidual = FCL - Distribuições
\]

FCL non-GAAP divulgado deve permanecer em:

~~~text
REPORTED
~~~

---

### CALC-11 — Sinais, escala e zero

A regra de cada item deve declarar:

- sinal contábil;
- escala;
- unidade.

Divisão por zero resulta em:

~~~text
NAO_CALCULAVEL
~~~

Nunca deve resultar em infinito.

---

### CALC-12 — IFRS/US GAAP

Diferenças não devem ser “corrigidas” genericamente.

Cada ajuste deve registrar:

- norma;
- item afetado;
- efeito;
- regra;
- reconciliação.

Divergência sem reconstrução defensável reduz comparabilidade.

---

### CALC-13 — M&A e restatements

Aquisições, alienações e mudanças de perímetro devem gerar flags:

~~~text
M&A
~~~

e visões reportada/orgânica quando defensáveis.

Restatement cria nova versão.

Períodos impactados são recalculados sem apagar valores anteriores.

---

### CALC-14 — Estados

Estados possíveis:

~~~text
ALTA
MEDIA
BAIXA
NAO_COMPARAVEL
NAO_DISPONIVEL
NAO_CALCULAVEL
~~~

Todos exigem justificativa.

---

## 13. Mapeamento mínimo empresa × KPI

| Empresa | Particularidades obrigatórias |
|---|---|
| Petrobras | Mapear DFC para FCO, CAPEX, dividendos e recompras; balanço para caixa, financiamentos e leases; DRE/notas para EBIT, DD&A, imposto e EBITDA; preservar ROCE reportado. |
| Equinor | Mapear CFO, organic CAPEX, finance debt, lease liabilities, cash/investments, dividends paid, buybacks, adjusted operating income e tax; sinalizar timing fiscal. |
| Chevron | Mapear CFFO, CAPEX, cash/debt, ROCE, dividends, repurchases, DD&A e special items; registrar US GAAP e mudanças de perímetro. |
| Shell | Mapear CFO, cash CAPEX, total/net debt, leases, ROACE, dividends, buybacks e adjusted EBITDA; sinalizar trading e capital de giro. |

Locator exato deve ser configurado por documento e trimestre.

Não pode ficar apenas em comentário de código.

---

## 14. Pipeline e operação

~~~text
discover
→ download/upload
→ validar tipo/tamanho
→ SHA-256
→ persistir original
→ extrair
→ validar schema
→ persistir bruto
→ normalizar
→ converter FX
→ calcular trimestre/LTM
→ qualidade
→ reconciliar
→ aprovar
→ publicar Parquet/DuckDB
→ atualizar web
→ exportar dataset Power BI
→ arquivar evidências
~~~

### 14.1 Idempotência

Chave lógica:

~~~text
empresa
+ período
+ tipo documental
+ versão
+ item
+ locator
~~~

Mesmo hash:

~~~text
NO_CHANGE
~~~

Hash novo:

~~~text
nova versão
~~~

### 14.2 Falhas

- timeout;
- três tentativas configuráveis;
- backoff;
- quarentena.

### 14.3 Reprocessamento

Deve ser possível reprocessar por:

- empresa;
- período;
- documento;
- versão de regra.

### 14.4 Logs

Cada execução deve registrar:

~~~text
timestamp
run_id
etapa
empresa
período
severidade
duração
mensagem
exceção
~~~

---

## 15. Dashboard web

Páginas obrigatórias:

1. resumo executivo;
2. posição e trajetória;
3. comparação por KPI;
4. drivers e contexto;
5. ponte de caixa;
6. qualidade e comparabilidade;
7. metodologia e fontes;
8. regras e restatements;
9. administração da carga/upload.

Filtros:

- empresa;
- período;
- KPI;
- reportado/padronizado;
- leases;
- versão.

Tooltips devem apresentar:

- definição;
- interpretação;
- fonte;
- limitações.

A metodologia deve navegar de:

~~~text
KPI
→ regra
→ componentes
→ ajustes
→ documento
~~~

---

## 16. Power BI local

O arquivo Power BI:

- consome Parquet ou exportação tabular curada do RADAR;
- não integra container, VPS ou autenticação web;
- replica páginas 1–8 e filtros do dashboard web;
- preserva IDs de lineage e links públicos;
- não recalcula regras financeiras em DAX quando já disponíveis no dataset.

### 16.1 Tema

~~~text
dataColors:
#008542
#FDC82F
#006298
#00B2A9
#A8B400
#FEDF00
#E17000
#675C53
#004165
#7D9AAA

background: #FFFFFF
foreground: #008542
tableAccent: #00B2A9
~~~

A ordem de cores orienta séries, mas o mapeamento empresa-cor deve ser configuração estável e documentada.

---

## 17. Branding e acessibilidade

### 17.1 Cores

Cores principais:

~~~text
Verde:   #008542
Amarelo: #FDC82F
Branco:  #FFFFFF
~~~

Cores de apoio:

~~~text
#00B2A9
#C4D600
#EBFF00
#ED8B00
#006298
#3DDAFF
#75787B
#000000
~~~

### 17.2 Tipografia

Utilizar pilha tipográfica:

~~~css
font-family: system-ui, sans-serif;
~~~

Não existe requisito de fonte proprietária ou específica.

### 17.3 Composição

- branco como base preferencial;
- títulos preferencialmente à esquerda;
- até três grandes superfícies estruturais coloridas;
- séries analíticas não estão sujeitas ao limite de três cores;
- percentuais de 25%, 50% e 75% permitidos em gráficos e tabelas;
- gradiente somente linear;
- gradiente deve manter aproximadamente 60% a 70% de cor principal;
- evitar combinação predominante de amarelo ou laranja com azul claro ou azul escuro;
- cor não pode ser o único mecanismo de transmissão de significado.

### 17.4 Acessibilidade

A aplicação web deve atender **WCAG 2.2 nível AA**.

Critérios mínimos:

- contraste de pelo menos `4.5:1` para texto normal;
- contraste de pelo menos `3:1` para texto grande;
- contraste de pelo menos `3:1` para componentes gráficos e controles relevantes;
- navegação por teclado;
- foco visível;
- zoom de 200%;
- reflow em viewport de 320 px, exceto visualizações inerentemente bidimensionais;
- alvo mínimo de 24 × 24 px quando aplicável;
- informação essencial não pode depender exclusivamente de cor.

### 17.5 Logomarca

A proibição da logomarca Petrobras aplica-se exclusivamente aos artefatos produzidos pelo RADAR, incluindo:

- interface web;
- dashboard;
- tela de login;
- favicon;
- relatórios gerados;
- exportações geradas;
- apresentações geradas;
- elementos decorativos;
- demais saídas produzidas pela aplicação.

Documentos-fonte originais e evidências documentais preservadas estão isentos dessa proibição e devem permanecer íntegros.

A logomarca existente nesses documentos não pode ser reutilizada como elemento de branding.

O favicon:

- pode ser próprio;
- pode ser inexistente;
- não pode conter, reproduzir, derivar ou imitar a logomarca Petrobras.

---

## 18. Segurança

- senha compartilhada armazenada como hash em variável externa;
- comparação em tempo constante;
- segredo de sessão externo;
- cookies com `Secure`, `HttpOnly` e `SameSite=Lax`;
- HTTPS obrigatório no VPS;
- proteção CSRF em formulários;
- rate limit simples no login;
- nenhuma rota funcional anônima;
- `/health` pode retornar apenas estado técnico mínimo;
- arquivos carregados nunca devem ser executados;
- conteúdo oculto ou instruções em fontes nunca devem alterar regras;
- utilizar:

~~~text
X-Robots-Tag: noindex, nofollow
~~~

---

## 19. Qualidade e requisitos não funcionais

Checks mínimos:

- completude;
- unicidade;
- tipo;
- sinal;
- escala;
- moeda;
- período;
- integridade;
- quatro trimestres;
- hash;
- reconciliação;
- vigência;
- variação;
- comparabilidade.

Estados:

~~~text
APROVADO
ALERTA
REVISAO
BLOQUEADO
~~~

A solução deve:

- ser determinística;
- suportar histórico sem mudança de schema;
- preservar dados após recriação do container;
- manter configuração externa;
- registrar versão do código;
- registrar versão das regras.

Meta de desempenho permanece:

~~~text
OPEN-04
~~~

e deve ser aprovada antes do teste final.

---

## 20. Testes

| Grupo | Critérios |
|---|---|
| Financeiro | Golden tests para CALC-01–14; tolerância monetária configurada e documentada. |
| Ingestão | Contratos de layout, hash, fallback e arquivo alterado. |
| Dados | Chaves, tipos, integridade e idempotência. |
| Restatement | Versão antiga recuperável e impacto recalculado. |
| E2E | Fonte pública → dashboard web → lineage. |
| Auth | Anônimo e senha inválida negados; válida permitida; segredo ausente da imagem. |
| Container | Build limpo, health check, volumes e restauração. |
| Acessibilidade | axe-core equivalente + teclado manual; WCAG AA; zoom 200%; viewport 320 px. |
| Branding | Tokens, tema Power BI, consistência e ausência de logomarca nos artefatos gerados. |
| Power BI | Consumo do mesmo dataset, páginas, filtros e lineage coerentes. |
| Reprodutibilidade | Execução em máquina limpa seguindo runbook. |

---

## 21. Runbook

~~~bash
git clone <repositorio>
cd radar
cp .env.example .env
docker compose build
docker compose run --rm radar pytest
docker compose up -d
docker compose exec radar flask radar ingest --from 2025Q3 --to 2026Q2
docker compose exec radar flask radar process --from 2025Q3 --to 2026Q2
docker compose exec radar flask radar validate --from 2025Q3 --to 2026Q2
docker compose exec radar flask radar publish
~~~

O runbook deve cobrir:

- carga inicial;
- trimestre novo;
- upload;
- reprocessamento;
- alteração de regra;
- rollback;
- logs;
- atualização Power BI;
- HTTPS;
- troca de senha;
- diagnóstico.

### 21.1 Backup

Backup mínimo:

~~~text
data/
database/
evidence/
configurações não secretas
~~~

### 21.2 Restauração

A restauração deve exigir apenas:

- volumes;
- repositório;
- nova configuração de segredos.

---

## 22. Entregáveis

| ID | Entregável |
|---|---|
| ENT-01 | Aplicação web RADAR |
| ENT-02 | Power BI local |
| ENT-03 | Catálogo de fontes |
| ENT-04 | Catálogo de métricas e regras |
| ENT-05 | DuckDB/Parquet |
| ENT-06 | Evidências |
| ENT-07 | Runbooks |
| ENT-08 | Dockerfile/Compose |
| ENT-09 | Modelo de dados e dicionário |
| ENT-10 | Diagramas |
| ENT-11 | Testes |
| ENT-12 | ADRs |
| ENT-13 | Riscos e decisões abertas |
| ENT-14 | Tema e tokens |
| ENT-15 | Apresentação de 15 minutos |
| ENT-16 | Documentação de implantação e sustentação |

---

## 23. ADRs

### ADR-01 — Python + Flask + Dash

Utilizar Python, Flask e Dash, sem SPA independente.

### ADR-02 — DuckDB + Parquet

Utilizar DuckDB e Parquet como persistência principal.

### ADR-03 — Um container RADAR

Utilizar um único container para aplicação web e pipeline sempre que possível.

### ADR-04 — Power BI local e paralelo

Power BI deve permanecer fora do container, do VPS e da autenticação web.

### ADR-05 — Git agnóstico de provedor

O projeto deve utilizar Git sem dependência de provedor corporativo.

### ADR-06 — CLI sem orquestrador

Processos operacionais devem ser executáveis por CLI Python.

### ADR-07 — VPS + reverse proxy HTTPS

A aplicação web deve poder ser implantada em VPS Linux convencional.

### ADR-08 — Senha compartilhada

A autenticação da PoC deve utilizar uma única senha compartilhada.

### ADR-09 — Tema centralizado e fonte de sistema

Branding deve ser centralizado em configuração reutilizável e utilizar fonte de sistema.

### ADR-10 — Logomarca

A logomarca Petrobras é proibida somente nos artefatos produzidos pelo RADAR.

---

## 24. Riscos e decisões abertas

| ID | Item |
|---|---|
| RISK-01 | Mudança de layout: adapter e teste de contrato. |
| RISK-02 | Bloqueio de download: upload manual. |
| RISK-03 | Falsa comparabilidade: flags e sensitivities. |
| RISK-04 | M&A/restatement: versionamento e visão orgânica. |
| RISK-05 | Vazamento de senha: hash externo e rotação. |
| RISK-06 | Perda do VPS: backup restaurável. |
| RISK-07 | Uso acidental de logomarca: inspeção de saídas. |
| OPEN-01 | Confirmar prazo de entrega. |
| OPEN-02 | Selecionar fonte pública oficial de câmbio. |
| OPEN-03 | Aprovar hierarquia do imposto operacional no ROCE. |
| OPEN-04 | Definir meta de desempenho no VPS de referência. |
| OPEN-05 | Confirmar tratamento de goodwill e híbridos por sensibilidade. |
| OPEN-06 | Definir mapeamento cromático estável das empresas. |

---

## 25. Rastreabilidade e aceite

Matriz obrigatória:

~~~text
CASE
→ regra
→ requisito
→ componente
→ entidade/campo
→ transformação
→ visual
→ teste
→ evidência
~~~

A PoC será aceita quando:

1. quatro empresas estiverem carregadas;
2. houver pelo menos quatro trimestres comuns;
3. os cinco KPIs estiverem calculados;
4. FCL estiver calculado;
5. `CALC-01` a `CALC-14` estiverem testados;
6. reportado, padronizado e sensibilidades coexistirem;
7. os dados utilizados nos cálculos e análises vierem de fontes públicas;
8. lineage estiver navegável;
9. metodologia estiver navegável;
10. novo trimestre não exigir remodelagem;
11. web e Power BI consumirem o mesmo dataset curado;
12. container sobreviver à recriação sem perda de dados persistentes;
13. aplicação web exigir senha;
14. aplicação web utilizar HTTPS quando publicada;
15. Power BI permanecer local;
16. acessibilidade WCAG 2.2 AA estiver validada;
17. artefatos produzidos pelo RADAR não contiverem logomarca Petrobras;
18. documentos-fonte originais permanecerem íntegros;
19. regras financeiras estiverem versionadas;
20. restatements preservarem versões anteriores;
21. aproximações silenciosas não existirem;
22. outro engenheiro conseguir reproduzir a solução seguindo o runbook;
23. um coding agent externo conseguir implementar a solução sem acesso a documentos, arquivos ou serviços internos.

---

## 26. Tese arquitetural

> **O RADAR deve concentrar complexidade na comparabilidade financeira, qualidade e rastreabilidade — não na infraestrutura.**

~~~text
Fontes públicas
      ↓
Python
      ↓
Documentos originais imutáveis
      ↓
Extração e fatos brutos
      ↓
DuckDB / Parquet
      ↓
Regras versionadas
      ↓
Normalização
      ↓
KPIs comparáveis
      ↓
Qualidade + reconciliação + lineage
      ↓
Dataset analítico curado
      ├──────────────────────────────┐
      ↓                              ↓
Flask + Dash                    Power BI local
      ↓                         entregável paralelo
Container OCI
      ↓
Reverse proxy + HTTPS
      ↓
Senha compartilhada
      ↓
VPS
~~~

A aplicação deve transformar fontes heterogêneas em inteligência comparável, preservando transparência suficiente para que cada conclusão possa ser explicada, reproduzida e contestada.

A arquitetura deve evitar complexidade que não contribua diretamente para:

- comparabilidade financeira;
- qualidade;
- rastreabilidade;
- reprodutibilidade;
- segurança proporcional à PoC;
- clareza da visualização;
- facilidade de implantação e manutenção.

O **RADAR web** constitui a aplicação autocontida principal.

O **Power BI** constitui um entregável analítico local e paralelo, alimentado pelo mesmo dataset curado, sem fazer parte do container, do VPS ou do fluxo de autenticação da aplicação web.