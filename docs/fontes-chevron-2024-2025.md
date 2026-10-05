# Chevron — fontes 2024–2025

Baixados os oito releases oficiais trimestrais, preservados na prévia local
com URL, período e SHA-256. Inventário: config/ingestion/chevron-sources-2024-2025.json.
Índice oficial: https://chevroncorp.gcs-web.com/node/5986
Não houve publicação financeira nem deploy.

## Mapeamento inicial

- FCO: Net Cash Provided by Operating Activities; não substituir por CFFO
  excluding working capital ou adjusted free cash flow.
- CAPEX: Capital expenditures na DFC; aquisição de negócios e ações Hess
  em linhas distintas, fora de CAPEX orgânico. Não somar Affiliate Capex
  automaticamente: investimento dos parceiros não equivale a aporte de caixa.
- Distribuições: Cash dividends — common stock + Shares repurchased
  na DFC; conferir liquidação, impostos e footnotes. Compra de ações Hess
  é aquisição, não recompra Chevron.
- Dívida: separar finance lease liabilities da dívida e operating leases
  para a sensibilidade; não copiar net debt-to-CFFO como dívida/EBITDA.
- EBIT/EBITDA: reconstruir ajustes antes de impostos, excluir financeiro
  e preservar investidas líquidas conforme perímetro. Adjusted earnings
  é lucro líquido, não NOPAT nem EBITDA.
- Imposto: hierarquia aprovada, sem estender alternativa Petrobras 34%
  nem aplicar taxa fictícia Chevron 10% aos dados reais.
- 2025 inclui aquisição Hess; registrar mudança de perímetro na evolução
  sem fabricar histórico pro forma para 2024.

## Precisão e próximos componentes

Os releases apresentam DFC resumida preliminar em US$ bilhões (uma casa
decimal). É necessário cruzar 10-K/10-Q para valores em milhões e notas
de dívida, goodwill e leases, com conciliação dos acumulados/trimestres.
Consulta CompanyFacts CIK 93410 concluída com contato autorizado
radar-benchmark@engineer.felipeloliveira.com.br. Snapshot SEC preservado
com hash c09b160603412cb45acf1bb9bf3732e531dedfb548afa0e275fd8aefd7ab397e.
Identidade confirmada: Chevron Corp. API inclui vários exercícios; o mapeamento
financeiro deve selecionar explicitamente 2024–2025, datas e accession.
A identificação pessoal encontrada no Git não foi enviada.

## Carga financeira preparada

Lotes em REVISAO na Administração da Carga local:
- 2024: ddfce867afda44918c87c9749ef86a6c, chevron-2024-statutory-cash-v1.
- 2025: 7e79002bb52149358cb74b87cab761a0, chevron-2025-statutory-cash-v1.

32 componentes (FCO, CAPEX, dividendos pagos e compras de ações),
16 conciliações independentes FCO/CAPEX com releases, todas aprovadas.
Acumulados YTD em USD convertidos em trimestres antes do LTM.
Accessions originais explicitamente selecionados. Arredondamento específico
do release US$50mi (uma casa em bilhões), sem modificar tolerância global.
48 testes passaram.

| Indicador | 2024 | 2025 | Estado |
|---|---:|---:|---|
| FCO (US$ mi) | 31.492 | 33.939 | Base estatutária |
| CAPEX pago (US$ mi) | 16.448 | 17.347 | Não comparável |
| Dividendos comuns pagos (US$ mi) | 11.801 | 12.751 | Caixa pago |
| Compras de ações (US$ mi) | 15.229 | 12.079 | Não comparável |
| CAPEX/FCO | 52,2291% | 51,1123% | Não comparável |
| Distribuições/FCO | 85,8313% | 73,1607% | Não comparável |

CAPEX inclui fixed asset ou investment accounts segundo 10-K; M&A
e ações Hess excluídas, mas a segregação integral de investments orgânicos
e aportes JV não comprovada. CAPEX/FCO, FCL e residual preservam alertas.

Compras de ações incluem share repurchase e deferred compensation plans
(retenção para impostos de participantes); falta segregação. Excise tax
separado (US$145mi/146mi) não somado, nem compras de ações Hess.

Indisponíveis nesta carga: ROCE (ponte EBIT ajustado/imposto e capital),
dívida/EBITDA (EBITDA e saldos sem leases ainda não mapeados), sensibilidades
de leases/goodwill/JV. Pendência de mapeamento não equivale a inexistência
de fontes. Não aplicar 34% Petrobras ou taxa sintética 10% à Chevron.

Hess altera perímetro em 2025; evolução não pro forma. FCO preserva
classificação US GAAP de juros/dividendos sem normalização IFRS automática.
Os 10-K 2024/2025 foram preservados como evidência adicional.
Nada aprovado/publicado automaticamente ou implantado na VPS.
Selecionar os IDs acima; tentativas anteriores do histórico não publicar.

## Alternativa CAPEX orgânico aprovada — regra 1.9.0

Usar os valores trimestrais publicados pela Chevron, mantendo os investimentos operacionais da Hess após a aquisição. Excluir, pela definição da companhia, aquisições, bônus de concessão e custos de criação de novos negócios. Essa definição não tem equivalência integral comprovada à base RADAR: manter **NÃO COMPARÁVEL**. O valor pode ser calculado; não entra na série comparável.

| US$ bilhões, arredondados | Q1 | Q2 | Q3 | Q4 | Soma trimestral | Anual divulgado |
|---|---:|---:|---:|---:|---:|---:|
| 2024 | 4,0 | 3,9 | 4,0 | 4,1 | 16,0 | 15,9 |
| 2025 | 3,5 | 3,5 | 4,4 | 5,1 | 16,5 | 16,5 |

Os manifests `chevron-2024-organic-capex.json` e `chevron-2025-organic-capex.json` preservam URLs e SHA-256 das oito apresentações oficiais. A extração seleciona explicitamente a segunda parcela da célula “Total capex / Organic capex”, com validação do formato. Não há rateio nem ajuste artificial para fechar o anual. Cada número é publicado com uma decimal em bilhões; a ponte de quatro trimestres contra anual admite até US$ 250 milhões de arredondamento acumulado (5 × US$ 50 milhões), sem alterar a tolerância geral. Diferenças observadas: US$ 100 milhões em 2024 e zero em 2025; ambas conciliadas.

Lotes suplementares preparados, sem publicação automática:

- 2024: `97b15de677da40e8b7d16d780f40cb45`.
- 2025: `8c521a0fd58f416cbefea88bfde74751`.

Aprovar/publicar os lotes financeiros de caixa já identificados acima e, em seguida, esses suplementos: substituem somente CAPEX. Com FCO estatutário, CAPEX/FCO no fechamento anual resulta em aproximadamente 50,81% em 2024 e 48,62% em 2025. O cálculo de 2024 usa a soma trimestral de 16,0, não o anual arredondado de 15,9.

A proxy 2026 (https://chevroncorp.gcs-web.com/static-files/c5f428fb-436a-44e7-abf4-a4fbdadf8adf, p.63–64) apresenta CAPEX orgânico consolidado de US$ 16,5 bilhões e US$ 14,4 bilhões em resultados que excluem substancialmente a Hess. A diferença aproximada de US$ 2,1 bilhões serve apenas como contexto anual: não é uma ponte exata nem segregação trimestral e não é subtraída da base. As ações Hess adquiridas e a contraprestação sem caixa da combinação não são investimento operacional pós-aquisição e não devem ser retiradas novamente do CAPEX.

JV: affiliate capex representa investimentos realizados pelas afiliadas na participação Chevron, não necessariamente aportes de caixa da Chevron; não utilizá-lo automaticamente na sensibilidade de aportes orgânicos em JV. ROCE e dívida líquida/EBITDA continuam dependentes de seus próprios mapeamentos e conciliações; esta alternativa não os habilita.

## Investigação para equivalência ao CAPEX RADAR

Revisão de 05/10/2026: a nota 3 (Information Relating to the Consolidated Statement of Cash Flows) do 10-K 2025 fornece a seguinte decomposição de caixa, em US$ milhões, com comparativo 2024:

| Componente | 2024 | 2025 |
|---|---:|---:|
| Adições a imobilizado | 15.544 | 16.830 |
| Adições a investimentos | 573 | 225 |
| Desembolsos de poços secos do exercício | 331 | 292 |
| Total CAPEX na DFC | 16.448 | 17.347 |

As duas somas fecham exatamente. A nota explicita exclusão de movimentos sem caixa do imobilizado (395 em 2024; 1.235 em 2025); não deduzir novamente. Fonte preservada: https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/cvx-20251231.htm.

Essa abertura **não é uma conciliação completa do orgânico**. Não assumir que toda adição a investimentos é aporte orgânico em JV, nem que todo imobilizado é orgânico: direitos adquiridos e bônus de concessão podem estar capitalizados. Tampouco retirar automaticamente poços secos de um agregado já construído como desembolso de investimento, sem confrontar a regra dos peers.

Evidências adicionais nas apresentações oficiais preservadas:

- 2024 Q4, p.4: inorgânico anual de aproximadamente 530 milhões, principalmente aquisições de direitos e investimentos em novas energias. A diferença entre total exato 16.448 e orgânico anual arredondado 15.900 (548) não é uma medida exata dessas exclusões.
- 2025 Q1, p.5: inorgânico de aproximadamente 400 milhões, principalmente parceria de energia para data centers. Não informa segregação entre aquisição/aporte e implantação de ativos.
- 2025 Q2, p.8: inorgânico de aproximadamente 200 milhões, principalmente aquisição de áreas de lítio. O comunicado de 17/06/2025 confirma aquisição de direitos da TerraVolta e ETNR, mas não informa o preço exato: https://chevroncorp.gcs-web.com/news-releases/news-release-details/chevron-enters-domestic-lithium-sector-support-us-energy.
- 2025 Q4, p.6 e p.31: definição exclui aquisição, bônus de concessão e criação de novos negócios; não fornece ponte completa por natureza e trimestre.

Conclusão: manter a alternativa publicada NÃO COMPARÁVEL até obter ponte trimestral documentada que (a) retire aquisições/aplicações financeiras/aportes fora da base e (b) mantenha implantação orgânica de ativos consolidados, inclusive negócios novos. Ser classificado como “inorgânico” pela Chevron não basta para justificar exclusão RADAR. Não alterar metodologia apenas para obter o selo comparável. Hess pós-aquisição permanece no perímetro aprovado.

## Saldos para ROCE e dívida líquida — carga suplementar

Manifest `chevron-2024-2025-balances.json`; lote preparado `72297f20ea664bb4b33b1404c30d2899`: 50 pontos, sem erro de extração e seis pontes anuais aprovadas com diferença zero. Contém dívida CP/LP, caixa e equivalentes (excluindo restrito), caixa não operacional como aproximação PoC de 100% do caixa, patrimônio incluindo NCI e goodwill dos oito trimestres. Nas datas anuais, leases financeiros são retirados por prazo; a sensibilidade preserva a soma dos leases operacionais e financeiros. Fonte: os oito 10-Q/10-K oficiais, com SHA-256 e seletores explícitos, além do CompanyFacts SEC.

| US$ milhões | 2024Q4 | 2025Q4 |
|---|---:|---:|
| Dívida CP divulgada | 4.406 | 977 |
| Dívida LP divulgada | 20.135 | 39.781 |
| Leases financeiros CP | 58 | 786 |
| Leases financeiros LP | 546 | 659 |
| Dívida financeira sem leases | 23.937 | 39.313 |
| Caixa e equivalentes | 6.781 | 6.293 |
| Dívida líquida RADAR | 17.156 | 33.020 |
| Patrimônio incluindo NCI | 153.157 | 192.176 |
| Capital empregado reconstruído | 170.313 | 225.196 |
| Leases operacionais + financeiros | 5.674 | 7.430 |

A Chevron reclassifica certas obrigações com vencimento em até um ano para LP por intenção/capacidade de refinanciamento. Usar CP/LP apresentados no balanço, sem somar novamente DebtCurrent aos totais. Em particular, DebtCurrent de 10.918 em 2025 NÃO pode ser somado a LP de 39.781: duplicaria dívida reclassificada. Os CP/LP divulgados somam 40.758, incluindo 1.445 de leases financeiros. Caixa restrito e depósitos a prazo não são misturados com caixa e equivalentes na base aprovada.

Não extrapolar leases anuais para Q1–Q3. A dívida publicada nesses trimestres mantém `includes_leases=true`; sem abertura de leases, o cálculo de dívida líquida sem leases e capital permanece indisponível. Isso também impede o capital médio LTM, mesmo com fechamento anual disponível. EBITDA normalizado ainda não foi carregado.

Decisão anterior, substituída pela aprovação documentada abaixo: **não utilizar o numerador alternativo do ROCE Chevron** (lucro ajustado + NCI + juros após imposto). Manter ROCE indisponível até reconstruir EBIT ajustado e imposto operacional compatível. Imposto consolidado da demonstração não é imposto operacional por si só. Não usar alíquota sintética de 10%, nem aplicar alternativa Petrobras ou Total automaticamente.

## Distribuições — investigação adicional

Os suplementos Excel oficiais reproduzem shares repurchased em bilhões arredondados; não fornecem abertura de leases nem segregação exata de caixa para retenções de empregados. Os 10-Q/10-K trazem a tabela `Issuer Purchases of Equity Securities` com quantidade total, quantidade do programa e preço médio de todas as compras. A nota confirma inclusão de compras dos participantes dos planos de remuneração para retenção de imposto.

Exemplo comprovado 2024Q1: 19.737.687 ações totais versus 19.734.180 do programa, diferença de 3.507; a diferença ocorre em janeiro (6.910.470 totais versus 6.906.963 do programa). O preço médio mensal de US$ 146,56 se aplica ao conjunto, não especificamente às 3.507 ações. Multiplicar a diferença pelo preço médio seria uma estimativa, não segregação exata de caixa liquidado. Tampouco confundir tabela de compras com conciliação de liquidação na DFC.

Conclusão desta revisão: dividendos pagos continuam elegíveis; recompra/distribuições mantêm NÃO COMPARÁVEL até conciliar caixa exclusivo do programa e eventual saldo de liquidação. Não remover retenções por aproximação sem decisão explícita, nem somar excise tax, ações Hess ou distribuições a NCI ao agregado aprovado de acionistas comuns.

## Revisão aprofundada das lacunas — 05/10/2026

O inventário agora preserva os oito suplementos oficiais XLSX com SHA-256. Revisados em conjunto com os oito 10-Q/10-K, releases, apresentações e a estrutura inline XBRL dos próprios filings (não somente CompanyFacts). Resultado estruturado em `chevron-comparability-evidence-2024-2025.json`; este arquivo é evidência de pesquisa, não manifest financeiro para publicação.

### Recompras fora do programa

| Trimestre | Total de ações compradas | Ações do programa | Fora do programa |
|---|---:|---:|---:|
| 2024Q1 | 19.737.687 | 19.734.180 | 3.507 |
| 2024Q2 | 19.034.424 | 19.034.311 | 113 |
| 2024Q3 | 32.209.398 | 32.209.398 | 0 |
| 2024Q4 | 29.463.099 | 29.462.320 | 779 |
| 2025Q1 | 25.087.428 | 24.973.121 | 114.307 |
| 2025Q2 | 18.620.920 | 18.606.376 | 14.544 |
| 2025Q3 | 16.623.281 | 16.620.000 | 3.281 |
| 2025Q4 | 19.741.188 | 19.739.300 | 1.888 |

Fonte de cada linha: respectivo filing, tabela Issuer Purchases of Equity Securities, linha Total. Os números confirmam que as retenções não são uma hipótese meramente genérica. Em 2025Q1, não é defensável ignorar a parcela sem segregação. Em 2024Q3, o total corresponde integralmente ao programa; 32.209.398 × preço médio publicado de US$ 147,47 ≈ US$ 4.749,920 milhões, próximo ao caixa de US$ 4.750 milhões derivado da DFC. Essa conciliação de controle não estabelece por si só os saldos de liquidação nem a elegibilidade do LTM inteiro. Não promover automaticamente uma sequência LTM com outros trimestres ainda pendentes.

### EBIT e imposto

Juros e despesas da dívida antes de imposto: 594 em 2024 e 1.217 em 2025 (US$ milhões, DRE/MD&A). Juros após imposto usados na ponte ROCE da apresentação: 539 e 1.096. As diferenças aritméticas são 55 e 121. Esse é um avanço de evidência para a parcela financeira, mas depende de verificar correspondência de perímetro dos juros e não resolve imposto de receita financeira e dos demais componentes não operacionais. A nota 14/segmentos separa juros e receitas de juros em All Other, mas também mantém despesas corporativas e outros resultados nesse agregado: excluir todo All Other retiraria custos operacionais corporativos indevidamente. A tabela de itens especiais fornece pré-imposto/imposto/após-imposto para ajustes divulgados, mas não substitui a ponte do imposto financeiro remanescente. Não carregar imposto consolidado como operacional, nem inferir EBIT a partir do numerador alternativo (posteriormente aprovado).

### Leases e EBITDA

A inspeção dos fatos inline XBRL dos relatórios intermediários confirma ausência de fatos explícitos de FinanceLeaseLiability/OperatingLeaseLiability nas datas intermediárias examinadas; a menção a dívida **incluindo** leases não é sua segregação. Os suplementos XLSX também não abrem esses saldos. Mantêm-se os valores anuais comprovados e os trimestres pendentes. EBITDA não pode ser rotulado ajustado normalizado apenas pela soma de resultado antes de imposto, juros e DDA, sem excluir resultado financeiro e alinhar os mesmos itens especiais em EBIT/DDA.

Conclusão: a pesquisa produziu evidências adicionais e delimitou as lacunas, mas ainda não sustentou promoção dos índices LTM para COMPARÁVEL. Preservar dados e estados anteriores. A aprovação de alternativas/estimativas não equivale à comprovação de equivalência integral à regra comum.

## Conclusão da busca nas divulgações públicas examinadas

Após revisar também as oito transcrições oficiais de 2024–2025 e o 10-K 2025 integral de 353 páginas, incluindo anexos, a conclusão da investigação é **PUBLIC_DISCLOSURE_INSUFFICIENT_FOR_STRICT_COMPARABILITY**. O escopo e SHA-256 das fontes adicionais constam do inventário e do arquivo de evidências. Essa conclusão se limita às divulgações examinadas; não afirma que a informação nunca poderá ser publicada.

Há indeterminação de componentes, não somente um problema de parser:

1. **ROCE:** o imposto consolidado agrega componentes operacionais, financeiros e outros. As notas e reconciliações examinadas não fornecem todas as parcelas para reconstruir imposto compatível com EBIT normalizado. A Tabela III suplementar de produção usa impostos calculados por alíquotas estatutárias, em perímetro upstream, conforme explicação expressa na p.111 do PDF integral (p.110 impressa); não substitui imposto operacional consolidado. O numerador alternativo foi posteriormente aprovado para cálculo NÃO COMPARÁVEL.
2. **Dívida/capital trimestrais:** CompanyFacts e todos os fatos inline XBRL de leases foram confrontados nos oito filings. Os fatos de passivo de lease aparecem nos dois fechamentos anuais, mas não nos seis intermediários. Saldos inicial/final anuais, pagamentos e novas obrigações anuais não identificam seus movimentos por trimestre, especialmente com a aquisição Hess. Interpolação é estimativa, não conciliação.
3. **Distribuições:** a tabela permite separar quantidade de ações do programa e de planos, mas o preço médio é do conjunto. Mesmo conhecendo o custo agregado, faltam preços exclusivos das duas parcelas; é uma equação com duas incógnitas. A DFC conjunta acrescenta a necessidade de conciliar data da compra com caixa liquidado. Arredondamento da fonte e tolerância de conciliação não autorizam inventar a parcela ausente.
4. **CAPEX:** o agregado inorgânico inclui naturezas que exigem tratamentos distintos na base RADAR. A resposta da administração em 2025Q1 (transcrição p.12) discute contratação de turbinas, engenharia e implantação do negócio de energia, mas não fornece o preço exato ou a ponte contábil da parcela de aproximadamente 400 milhões. A caracterização como JV na pergunta da analista não comprova aporte de caixa por si só. Não aplicar exclusão integral nem inclusão automática como sensibilidade.

Concluída esta busca, não promover índices LTM para comparáveis nem alterar as decisões metodológicas para preencher lacunas. Para avançar com exatidão, seria necessário novo detalhamento **público** da Chevron (inclusive esclarecimento público de RI) dos componentes acima. Nenhuma comunicação ao RI foi enviada. Fontes primárias e dados já extraídos permanecem preservados; nenhuma publicação financeira foi feita por esta pesquisa.


### Alternativas aprovadas e implementadas em 05/10/2026

A aprovação posterior substitui a rejeição inicial do NOPAT alternativo. Usar `chevron-2024-2025-approved-alternatives.json`, e não o lote antigo de saldos com leases financeiros excluídos nos fechamentos anuais.

- ROCE: `Adjusted ROCE earnings` divulgado, conciliado com lucro ajustado + NCI + juros após imposto. Q4 é anual menos Q1–Q3; nunca usar a linha anualizada como fluxo trimestral. Capital médio = média da abertura e fechamento LTM, reconstruídos com patrimônio incluindo NCI + dívida publicada incluindo leases financeiros − caixa integral. Goodwill incluído na base.
- Dívida líquida/EBITDA: dívida acima menos caixa; EBITDA aproximado = lucro antes de impostos + despesas de juros/dívida + DDA estatutária. Ponte com lucro consolidado + imposto + juros + DDA. Mantém receitas financeiras e especiais; não constitui EBITDA ajustado normalizado.
- Sensibilidade leases: adicionar somente operacionais ao capital e à dívida, pois financeiros já estão na base. Saldos anuais de 2023–2025 disponíveis; saldos intermediários continuam ausentes, sem interpolação.
- CAPEX/FCO: preservar lotes de CAPEX orgânico divulgado já preparados. Mantém investimentos operacionais Hess após aquisição; não usar contraprestação da aquisição como ajuste adicional.
- Distribuições/FCO: DFC com dividendos + recompras, inclusive planos de empregados; excise tax e ações Hess excluídos. Preservar lotes de caixa existentes.

Todas essas alternativas continuam **NÃO COMPARÁVEIS**. A aprovação de metodologia não substitui revisão/publicação dos valores. Teste dos dados preparados: ROCE 2024 10,9307%, 2025 7,4470%; dívida líquida/EBITDA 0,3913x e 0,8387x, respectivamente.
