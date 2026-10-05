# Petrobras — ingestão 2025

Preparada em 05/10/2026, regras v1.8.0. Mapeamento executável
`config/ingestion/petrobras-2025.json`, `petrobras-2025-common-basis-v2`.
Lote `dfeb4c1d87f64a8fb5e59b7e6e8759b2`, **REVISAO** na prévia local
http://127.0.0.1:8052/upload. Não publicado financeiramente nem implantado na VPS.
68 componentes, 107 seletores e 21 conciliações com diferença zero. 46 testes
passaram; aprovação/publicação simuladas somente em banco isolado.

## Origem e rastreabilidade

[Central de resultados oficial](https://www.investidorpetrobras.com.br/resultados-e-comunicados/central-de-resultados/)
fornece as demonstrações e as planilhas dos quatro trimestres em BRL.
O índice público do RI identifica a Petrobras pelo tenant
`25fdf098-34f5-4608-b7fa-17d60b2de47d` do provedor MZ. O download foi
habilitado somente para esse caminho em `api.mziq.com`, não para outros
clientes do provedor. O catálogo original e cada publicação foram preservados;
URLs, SHA-256 e localizadores constam do mapeamento e da evidência do lote.

- XLSX trimestrais: abas DFC, DRE, Balanço Patrimonial,
  Reconciliação EBITDA ajustado e Indicadores de endividamento.
- PDF anual: DFC consolidada p.6, nota 16 (pagamentos antecipados),
  nota 18 (imposto), nota 24 p.82 (goodwill).
- PDFs trimestrais: nota de intangível p.34 (Q1), p.37 (Q2/Q3).
- Relatório de Desempenho 4T25 p.11: aquisição de direitos Mero/Atapu.

Cada publicação possui seletores próprios, com guards de período, unidade e
rótulo. Em Q1, por exemplo, FCO está em DFC!B34; em Q4, DFC!B35.
Não reutilizar números de linhas sem verificar a publicação. Traço em recompra
é explicitamente mapeado como zero, confirmado pela DFC anual; não inferir
zero para informações ausentes. Não há recompras em 2025.

## Câmbio aprovado

Fluxos já divulgados por trimestre em BRL: dividir cada trimestre pela média
aritmética dos fechamentos diários **PTAX venda Bacen**, depois somar LTM.
Saldos: PTAX venda de fechamento ou última publicação anterior. Snapshot
2025 cobre fluxos e saldos; snapshot 20–31/12/2024 cobre abertura.

| Trimestre | PTAX média R$/USD | FCO (R$ mi) | CAPEX pago divulgado (R$ mi) | Dividendos/JCP pagos (R$ mi) |
|---|---:|---:|---:|---:|
| Q1 | 5,8521524590 | 49.338 | 23.297 | 16.587 |
| Q2 | 5,6660606557 | 42.424 | 23.170 | 9.567 |
| Q3 | 5,4488439394 | 53.655 | 26.629 | 10.973 |
| Q4 | 5,3954890625 | 54.916 | 35.618 | 8.078 |
| Soma BRL | — | 200.333 | 108.714 | 45.205 |

Valores financeiros convertidos no banco isolado, antes de publicação:
FCO US$ 35.943,308 mi; distribuições/FCO 22,3514%; dívida líquida/EBITDA
0,470518x. O FCO difere dos US$ 36.047 mi publicados pela Petrobras porque
nossa conversão trimestral PTAX é a regra aprovada; não forçar igualdade com
a conversão da companhia.

Petrobras classifica juros pagos em financiamento e dividendos recebidos em
investimento, como informa a nota da DFC. FCO segue nossa definição estatutária;
normalização dessa classificação entre IFRS e US GAAP exigiria outra decisão.

## Dívida, capital e sensibilidades

Financiamentos CP/LP são divulgados separados de arrendamentos. Na base,
`includes_leases=false`. Dívida líquida RADAR = financiamentos CP + LP − caixa
e equivalentes; não copiar dívida líquida da companhia, que inclui
“disponibilidades ajustadas” e leases. Aplicações financeiras não foram
adicionadas ao caixa. PL total inclui NCI, sem duplicação. CE subtrai 100% caixa
conforme aproximação PoC aprovada.

Leases = obrigações correntes + não correntes do balanço, reconciliadas contra
total bruto em BRL no quadro de endividamento. Cinco saldos incluídos, de
2024Q4 a 2025Q4; não usar valores USD daquele quadro com moeda BRL.
Goodwill líquido também mapeado nos cinco saldos: R$ 124, 124, 123, 119 e
120 milhões. Aporte orgânico em JV não classificado: a linha de investimentos
agregada não entra na base nem vira zero na sensibilidade.

## EBIT e EBITDA na regra comum

A Petrobras remove resultado de investidas ao formar seu EBITDA ajustado.
Nossa regra mantém essa contribuição quando o investimento está no capital.
Não copiar a alternativa de EBITDA da TotalEnergies para a Petrobras.

EBIT ajustado RADAR = lucro antes do financeiro/participações/impostos da DRE
+ resultado de investidas + ajustes de impairment, alienações/baixas,
reciclagem por alienação quando divulgada e coparticipação identificados na
reconciliação da companhia. DD&A está separado do impairment na ponte e DFC.
Conjunto de ajustes: `PBR_IMPAIRMENT_DISPOSALS_COPARTICIPATION_KEEP_AFFILIATES`.
Não remover automaticamente todos os itens do EBITDA “sem eventos exclusivos”.

Controle independente em cada trimestre:
EBIT reconstruído = EBITDA ajustado divulgado − DD&A − exclusão das investidas
na ponte da Petrobras. DD&A da ponte é conferido com DD&A da DFC. A pipeline
agora aceita `reference_terms` para esse controle de referência composta, sem
permitir os mesmos fatos dos dois lados ou mistura de bases.

Em BRL, EBITDA RADAR anual = 237.177 − 242 = 236.935 milhões;
EBIT ajustado = 236.935 − 84.388 = 152.547 milhões. Converter os quatro
trimestres separadamente; não converter apenas esse total anual.

## Pendências reais

**CAPEX orgânico:** em dezembro a Petrobras desembolsou US$ 1,3 bilhão
(arredondado) para aumentar a participação nos direitos da União de Mero
(3,5%) e Atapu (0,95%). A nota 16 confirma o adiantamento, com contrato e
reconhecimento por competência previstos para 2026. A linha de caixa por
ativos incorpora essa saída em 2025. Não usar os R$ 9.692 mi de aumento total
em pagamentos antecipados como valor da aquisição: a nota diz “principalmente”
e o agregado inclui outros componentes.

Decisão aprovada: excluir como aquisição de participação em ativos da base
de CAPEX orgânico. A exclusão exige o valor exato em BRL; US$ 1,3 bi
arredondado não serve para ajuste final. Enquanto esse valor não for
identificado, preservar CAPEX/FCO divulgado de 54,4155%, FCL de
US$ 16.384,587 mi e residual de US$ 8.350,772 mi com **NÃO COMPARÁVEL**.

**ROCE padronizado:** nota 18 concilia IR/CSLL consolidado e taxa efetiva,
mas não isola imposto do financeiro e efeitos dos ajustes operacionais escolhidos.
Não usar alíquota nominal 34%, efetiva global 26,6%, imposto pago na DFC ou
alíquota fictícia 25%. EBIT, capital e sensibilidades foram preparados;
sem ponte fiscal defensável, ROCE permanece **NÃO COMPARÁVEL** e sem valor.
ROCE divulgado de 6,6% usa definição própria e não substitui o indicador.

Os pontos podem ser revisados e publicados pela Administração da Carga;
pendências de comparabilidade permanecem explícitas após publicação.

## Investigação fiscal adicional — 05/10/2026

O glossário do Relatório de Desempenho 4T25, p.43, define lucro operacional
após impostos a partir do EBITDA ajustado, DD&A dos ativos a câmbio histórico
e alíquota de 34% de IR/CSLL. Portanto, 34% possui fundamento na metodologia
pública da companhia; não corresponde ao imposto operacional efetivamente
incorrido nem reconstrói sozinho o ROCE divulgado.

A nota 12 (p.38) abre o financeiro líquido de R$ 4.971 mi entre receitas,
despesas, encargos capitalizados, desmantelamento e variações monetárias e
cambiais, mas não atribui IR/CSLL a cada item. A nota 18 (p.48–49) concilia
imposto total e apresenta saldos diferidos por natureza. A diferença dos saldos
diferidos entre anos não é despesa fiscal do período por natureza: há movimentos
em patrimônio líquido, conversão, utilização e outros. Não usar essa diferença
para reconstruir imposto financeiro ou imposto de impairment.

A tabela de eventos exclusivos do relatório apresenta efeito fiscal agregado
de R$ -4.728 mi em 2025, abrangendo um conjunto distinto dos nossos ajustes
(financeiro, câmbio, contingências, desmantelamento e outros). Não ratear esse
montante proporcionalmente para o conjunto de ajustes do RADAR.

Conclusão: não encontrada ponte integral comprovável de imposto operacional
incorrido. Alternativa recomendada, sujeita a aprovação: tributação normalizada
a 34% somente da contribuição operacional ajustada antes do resultado líquido
de investidas; manter a contribuição de investidas sem nova tributação, conforme
a regra vigente.

Exemplo anual de controle, em R$ milhões (não substituir conversão trimestral):
- EBIT ajustado com investidas: 152.547.
- Resultado líquido de investidas: -242.
- Base operacional estimada sujeita a imposto: 152.789.
- Imposto normalizado estimado: 51.948,26.
- NOPAT estimado: 152.789 × 66% - 242 = 100.598,74.

Identificação proposta: “NOPAT estimado com alíquota normalizada de 34%,
referenciada na metodologia Petrobras; capital reconstruído RADAR”. Manter
NÃO COMPARÁVEL até avaliação metodológica entre peers. Não mudar a regra
de competência para caixa, nem promover automaticamente a alternativa
a imposto operacional divulgado. Nenhum valor de imposto/NOPAT foi inserido
na carga enquanto a decisão está pendente.

## Alternativa fiscal aprovada e implementada

Usuário aprovou em 05/10/2026 a alternativa NORMALIZED_RATE exclusivamente
para Petrobras, registrada nas regras v1.8.0. A aplicação usa o EBIT ajustado
e o resultado líquido de investidas publicados, com perímetro idêntico, e
calcula imposto = (EBIT ajustado - investidas líquidas) × 34%. Sem os dois
componentes ou com perímetros divergentes, não calcula. Imposto divulgado
compatível ou NOPAT divulgado tem prioridade sobre a alternativa.

ROCE 2025 validado na carga preparada: 20,5601%, NÃO COMPARÁVEL.
68 componentes e 21 conciliações aprovadas pelos controles automáticos;
46 testes passaram. Lote continua em REVISAO para publicação financeira
e não foi implantado na VPS. As pendências fiscais anteriores neste documento
registram a investigação histórica; a alternativa normalizada agora está aprovada.

## Pesquisa adicional — valor Mero/Atapu

Comunicado Petrobras de 04/12/2025:
https://agencia.petrobras.com.br/pt/w/petrobras-informa-sobre-resultado-do-leil%C3%A3o-de-%C3%A1reas-n%C3%A3o-contratadas

PPSA confirma propostas vencedoras:
https://www.presalpetroleo.gov.br/leilao-de-areas-nao-contratadas/

Mero: proposta R$ 7.791.844.310,00; participação Petrobras 80%.
Atapu: proposta R$ 1.001.456.652,00; participação Petrobras 73,24%.
Parcela reconstruída com percentuais divulgados:
R$ 6.233.475.448,00 + R$ 733.466.851,9248 = R$ 6.966.942.299,9248.
O comunicado confirma pagamento previsto em dezembro de R$ 6,97 bilhões;
relatório anual confirma desembolso em dezembro (US$ 1,3 bilhão arredondado).

Valor reconstruído para escala financeira: R$ 6.966,9423 milhões,
arredondável a R$ 6.967 milhões. Não chamar de comprovante de pagamento
exato aos centavos: percentual de Atapu pode estar arredondado. Se 73,24%
foi arredondado a duas casas, incerteza de até R$ 50.072,83, abaixo de
US$ 1 milhão de tolerância aprovada. Reconstrução documentada permite
propor exclusão do preço de aquisição aprovado sem converter US$ arredondado.
A aplicação à carga exige substituir a pendência anterior com lineage
das propostas e percentuais, mantendo versões publicadas anteriores.
Nenhum ajuste foi publicado nesta etapa de pesquisa.

## Carga suplementar CAPEX pronta para publicação

Lote `2b793d9eed0c472098fc0e497d886524`, mapeamento
`petrobras-2025-organic-capex-v3`, em REVISAO na porta 8052.
Atualiza somente CAPEX 2025Q4, preservando os outros componentes e versões.
Fonte HTML oficial arquivada com SHA-256 e seletores numéricos com contexto
80%/73,24%. Duplicatas idênticas do texto na página são permitidas
explicitamente; valores divergentes ou contexto alterado bloqueiam extração.

Exclusão reconstruída R$ 6.966,9422999248 mi; CAPEX orgânico Q4
R$ 28.651,0577000752 mi; CAPEX anual R$ 101.747,0577000752 mi.
Conciliação com pagamento de R$ 6,97 bi arredondado: diferença
US$ 0,566714 mi, tolerância US$ 5,309621 mi; passou.
O valor não foi convertido a partir dos US$ 1,3 bi arredondados.
Comparabilidade do CAPEX marcada verdadeira após exclusão aprovada.
ROCE mantém alternativa fiscal não comparável. 47 testes passaram.
Lote preparado, não aprovado/publicado automaticamente e não implantado na VPS.
