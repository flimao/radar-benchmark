# Pipeline de dados reais

Implementada na branch `test-real-data`, regras v1.5.0. Executa no mesmo
container Python 3.12, sem Java, OCR, navegador automatizado ou novos pacotes.
Usa httpx, openpyxl, PyMuPDF, Decimal e DuckDB já instalados.

## Fluxo

1. Coletar documento/API ou usar original enviado na Administração de carga.
2. Preservar bytes por SHA-256. Registrar empresa, URL, localizador, período,
   padrão contábil, moeda, escala, conceito e versão do mapeamento.
3. Extrair por célula XLSX, rótulo/página/coluna PDF, filtro CSV, caminho JSON
   ou tag XBRL com datas, unidade e accession. Cabeçalhos XLSX/PDF são verificados.
   PDFs escaneados permanecem bloqueados; nenhum OCR/inferência silenciosa.
4. Normalizar sinais e escalas para milhões. Diferenciar fluxo trimestral,
   acumulado YTD e saldo. YTD menos YTD anterior compatível produz trimestre,
   com flag DERIVED_QUARTER. Não subtrair períodos de anos diferentes.
5. Aplicar ajustes documentados, conciliar pontes e converter BRL/USD.
6. Preparar lote em REVISAO e exibir fatos, evidências, divergências e alertas.
7. Responsável aprova campos elegíveis e justifica alertas. Publicação é uma
   ação separada; controles inválidos não podem ser dispensados pela aprovação.
8. Seletor **Base de dados → Reais · aprovados** consulta exclusivamente fatos
   reais publicados. Demonstração continua separada. Não há preenchimento com
   fatos sintéticos quando faltar componente real.

A preparação/publicação de um componente não garante disponibilidade de todos
os KPIs. A completude de quatro trimestres e os denominadores são verificados
por indicador na consulta. FCO pode estar disponível enquanto ROCE permanece
não comparável por imposto ausente. Publicações novas preservam versões
anteriores. A última publicação aprovada de cada campo/período é utilizada.

## Regras financeiras

- FCO estatutário inclui capital de giro. CFFO sem capital de giro e DACF
  preservam valor com NÃO COMPARÁVEL, sem substituir silenciosamente a base.
- CAPEX exige definição orgânica de caixa. Investimentos reportados com
  definição distinta mantêm valor não comparável até reconstrução documentada.
- Distribuições = dividendos pagos + recompras liquidadas. Valores declarados
  ou programas autorizados não são conceitos aceitos. NCI/cupons de híbridos
  não são automaticamente reclassificados como distribuição aos acionistas.
- EBITDA padronizado = EBIT ajustado + DD&A ajustado. Ambos exigem o mesmo
  conjunto de ajustes e perímetro; EBITDA reportado pode ser extraído para
  conciliação, mas não substitui automaticamente a reconstrução.
- Dívida líquida = dívida CP + LP sem leases − caixa/equivalentes. A presença de
  leases no total divulgado deve ser declarada explicitamente. Definições
  divergentes por prazo exigem abertura adicional e permanecem indisponíveis.
- Capital empregado = PL atribuível à controladora + NCI + dívida financeira
  sem leases − caixa não operacional. Se a fonte usa PL total incluindo NCI,
  NCI não é somado novamente. Híbridos seguem a classificação divulgada,
  incorporados aos saldos respectivos, sem adicionar outra vez o instrumento.
- ROCE = NOPAT LTM / média do capital inicial/final × 100. Saldos de abertura
  vêm do trimestre imediatamente anterior à janela. Goodwill permanece na
  base; sensibilidade o exclui dos dois saldos. Leases são adicionados nos
  saldos e dívida apenas na sensibilidade. Não se altera NOPAT automaticamente.
- Imposto real exige método DISCLOSED ou RECONSTRUCTED, fonte, reconciliação
  e mesmo conjunto de ajustes/perímetro do EBIT. Alíquotas fictícias nunca
  entram na base real. Sem imposto defensável, ROCE padronizado não comparável.
- Fluxos BRL: derivar trimestre em BRL, dividir pela média aritmética das PTAX
  venda de fechamento publicadas naquele trimestre, depois somar em USD.
- Saldos BRL: PTAX venda na data final ou última publicação anterior. Registrar
  data efetiva, cotação e fallback. Nenhuma taxa futura; demais moedas bloqueadas.
- A tolerância de conciliação é o maior de US$ 1 mi, 0,1% do valor de referência
  e arredondamento documentado. Referências independentes e ponte coerente com
  o componente são obrigatórias para reconstruções, ajustes, EBIT/DD&A/imposto.
- Variações >30% e anterior zero geram alertas que exigem aceitação justificada.
  Mudança de perímetro sem conciliação torna a comparação não comparável.

## Fontes/API

- Bacen: API PTAX OData, coletada por intervalos de até 366 dias. Preservar todos
  os boletins; filtrar Fechamento localmente. A implementação OData rejeitou
  `$filter` de tipoBoletim no teste real. Um dia entra uma vez na média;
  duplicatas idênticas são registradas/removidas, conflitantes bloqueadas.
- Yahoo Finance: séries diárias de contexto via chart API, sem pacote yfinance.
  Símbolos permitidos BZ=F, BRL=X, CVX, SHEL, TTE e PBR. Falhas/limites de acesso
  retornam indisponibilidade. BZ=F é futuro contínuo, não Brent físico;
  BRL=X não substitui PTAX. Não inferir margem de refino ou ROCE dessa API.
- SEC: API CompanyFacts financeira em JSON, sem chave. Configurar
  `RADAR_SEC_USER_AGENT` com aplicação e e-mail real de contato. O CIK é
  fornecido explicitamente e conferido no documento. Selecionar namespace,
  tag, unidade, datas, formulário/accession. Fatos ambíguos exigem ajuste do
  mapeamento; não se usa automaticamente o maior/latest valor. Conciliação
  e revisão também se aplicam a fatos XBRL.

Referências oficiais:
[Bacen](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDepin/gnastportal-dados-abertostaxas-de-cambio---todos-os-boletins-diarios.pdf),
[SEC](https://www.sec.gov/search-filings/edgar-application-programming-interfaces),
[TotalEnergies](https://totalenergies.com/investors/results).

`config/ingestion/companies.json` registra orientações específicas IFRS/US GAAP
para cada empresa. Os seletores são versionados por publicação. Um mapeamento
não é automaticamente reutilizado quando mudam hash, rótulos ou cabeçalhos.
Não há descoberta automática de todas as publicações das quatro empresas.

## Executar

No computador, na raiz do projeto:

```bash
# Preparar o exemplo real completo de FCO 2025. Não publica valores.
.venv/bin/python -m radar.ingestion prepare config/ingestion/totalenergies-2025.json --download
.venv/bin/python -m radar.ingestion list
.venv/bin/python -m radar.ingestion inspect ID_DO_LOTE

# APIs de contexto/conversão:
.venv/bin/python -m radar.ingestion ptax 2025-01-01 2025-12-31
.venv/bin/python -m radar.ingestion yahoo 'BZ=F' 2025-01-01 2025-12-31
# SEC: configurar e-mail de contato real antes de chamar.
.venv/bin/python -m radar.ingestion sec Chevron 93410
```

Em ambiente isolado, use `--data-dir /tmp/radar-ingestion-test` antes do comando.
Para disponibilizar nos indicadores após revisão do responsável:

```bash
.venv/bin/python -m radar.ingestion approve ID_DO_LOTE --reviewer 'Nome do responsável' --note 'Justificativa da revisão' --accept-alerts --fields cfo
.venv/bin/python -m radar.ingestion publish ID_DO_LOTE
```

A interface Administração de carga oferece preparação por JSON, inspeção,
aprovação e publicação. Para documentos já enviados, substituir `url`/formato
conforme a origem e usar `hash` com o SHA-256 exibido no upload. A interface
aceita hashes e não caminhos arbitrários no servidor. O download de documentos
pelo mapeamento é habilitado explicitamente na CLI por `--download`.

No container, use o volume do serviço. Para escrita por CLI, evite outro
processo escrevendo no mesmo DuckDB: pare o serviço, execute a carga e reinicie.

```bash
docker compose stop radar
docker compose run --rm radar python -m radar.ingestion prepare config/ingestion/totalenergies-2025.json --download
docker compose up -d radar
```

A revisão/publicação pela interface ocorre no mesmo processo do app e não
exige parada. Manter um worker Gunicorn para o DuckDB da PoC; mutações da
pipeline são serializadas entre threads. APIs opcionais e documentos falhos
mostram indisponibilidade e não produzem valores substitutos.

## Formato do mapeamento

Exemplos executáveis em `config/ingestion/totalenergies-2025q4.json` e
`config/ingestion/totalenergies-2025.json`. Documento: id, format, url, período
opcional e hash/path ou download explícito. `expected_hash` fixa a publicação.
Observação: id, document, period, period_type, currency, scale, basis, scope,
selector e, para publicação, field/concept. Observações sem field servem como
referências/ajustes independentes, sem publicação direta.

`adjustments` contém observation, coefficient e reason, sem eval/código.
`reconciliations` contém id, reference, terms (observation/coefficient),
applies_to, reason e rounding_usd_million opcional. `SUM_QUARTERS` permite
conciliar exatamente quatro trimestres com referência anual YTD do mesmo ano.
`fx` recebe hash de snapshot Bacen ou lista de hashes para intervalos adjacentes.

Selector XBRL JSON exemplo (accession precisa vir do filing efetivamente usado):

```json
{
  "taxonomy": "us-gaap",
  "tag": "NetCashProvidedByUsedInOperatingActivities",
  "unit": "USD",
  "where": {"start": "2025-01-01", "end": "2025-03-31", "form": "10-Q", "accn": "ACCESSION_DA_FONTE"},
  "guards": [{"path": ["cik"], "equals": 93410}]
}
```

O documento SEC também exige `issuer_cik`; valores XBRL monetários usam escala
`units`. Adapters não executam fórmulas do Excel: exigem valores calculados
salvos no documento e registram células sem cache como ausentes.

## Teste real realizado em 05/10/2026

Originais oficiais TotalEnergies: contas 2Q25 e 4Q25 + databook 4Q25.
FCO trimestral em US$ milhões: Q1 2.563, Q2 5.960, Q3 8.349, Q4 10.471.
Soma 27.343; DFC anual 27.343; diferença zero. PDF vs XLSX do Q4: diferença zero.
Os aumentos de Q2/Q3 geraram alertas >30%. O lote local permanece em REVISAO,
sem aprovação financeira pelo agente. Testes de aprovação/publicação usam
fixtures e banco temporário, sem publicar os resultados reais na VPS.

APIs reais: Yahoo BZ=F retornou 252 observações em 2025; Bacen retornou 252
fechamentos diários, com uma duplicata idêntica removida. Respostas originais
preservadas e snapshots registrados localmente. SEC testada com respostas
controladas; a chamada real requer contato configurado e não foi realizada.

A pipeline não foi implantada na VPS por esta alteração. A v0 publicada continua
na versão anterior. Mapeamentos reais completos de CAPEX, dívida, EBIT/DD&A,
imposto, goodwill e híbridos para os quatro peers precisam da revisão das
publicações específicas. Nenhum resultado foi inventado para completar ROCE.

Validação técnica final: 39 testes passaram localmente e no container Linux com
Python 3.12. A imagem de produção passou startup, saúde, autenticação, CSS,
layout Dash e exportação; original, lote de teste aprovado/publicado e banco
persistiram após recriação do container. Interface de inspeção de lote verificada
na prévia isolada em http://127.0.0.1:8052/upload. Essa prévia guarda cópia dos
originais e APIs em `/private/tmp/radar-ui-ingestion`, independente da VPS.

## Petrobras 2025

Mapeamento em `config/ingestion/petrobras-2025.json` e justificativas em
`docs/fontes-petrobras-2025.md`. O provedor documental MZ é reconhecido somente
no tenant Petrobras vinculado pelo RI oficial. Pontes aceitam `reference_terms`
para uma referência composta independente: mesmos período/tipo/moeda/perímetro,
fontes oficiais e nenhum fato compartilhado com os termos do cálculo. Continuam
valendo os controles de correspondência com os ajustes do componente.
