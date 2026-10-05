# Shell 2024–2025 — carga financeira e separação fiscal

Fontes oficiais preservadas: Quarterly Databook publicado em 30/07/2026, Annual Databook publicado em 12/03/2026 e Annual Report and Accounts 2025. Usar histórico consolidado mais recente; preservar versões e diferenças de arredondamento entre publicações. Valores USD milhões. IFRS.

Mapeamentos: `config/ingestion/shell-2024.json`, `shell-2025.json`. Lotes finais: 2024 `53b7f0e19c33476a8f907f096b8be819`; 2025 `987090af589c490090c1a1302110fcfb`. Cada lote tem 59 componentes sem bloqueios e oito pontes aprováveis. Lotes anteriores v1 são superados, não publicar.

FCO: Cash Flows linha 27, inclui capital de giro. Não usar FCO ex-capital de giro. Distribuições: linhas 49 e 51, dividendos Shell plc e recompras liquidadas; excluir dividendos NCI e ações em trust (linhas 50/53). Somas trimestrais versus anual conciliadas, com diferenças até USD 1 milhão.

CAPEX: linha 29 DFC, positivo para desembolso. Excluir aplicações em títulos e investimentos em JV da base. Permanece NÃO COMPARÁVEL: linha pode conter inorgânicos; a exclusão por categoria precisa ser conciliada. APM linha 44 divulga inorgânicos agregados, não assumir que tudo pertence somente à linha 29 nem subtrair em duplicidade. Nenhum aporte orgânico JV presumido.

Dívida líquida: APM dívida CP + LP − leases − caixa. Não usar net debt divulgado porque inclui derivativos e colateral adicionais. Capital: PL incluindo NCI + dívida sem leases − caixa integral (aproximação aprovada). Leases e goodwill disponíveis para sensibilidades, incluindo abertura 2023Q4.

EBIT: Sheet Shell earnings CCS + imposto CCS + juros ajustados − receita de juros − CCS investidas + CCS compras; reverte custo de reposição para custo histórico. Conciliar contra PBT estatutário, despesas/receitas financeiras e todos os itens identificados pré-imposto. DDA = DDA estatutária − impairment da mesma linha. Ajustment set único. EBITDA = EBIT + DDA, sem adicionar exploration well write-offs ordinários. Reconstrução segue regra comum; não é a alternativa de EBITDA divulgado rejeitada pelo usuário. As pontes passaram nos oito trimestres, sem ampliar tolerâncias.

## Impostos: duas dimensões, sem dupla contagem

A natureza corrente/diferida é diferente da origem operacional/financeira/especial. Não somar essas classificações como se fossem componentes independentes. Evidência com células/hash/valores em `shell-tax-evidence-2024-2025.json`.

- Corrente e diferido: annual Taxation charge linhas 6/7, somados conferem com total linha 8. Disponíveis anuais; não ratear em trimestres.
- Total trimestral de competência: quarterly Shell linha 24. Imposto pago na DFC não substitui esse total.
- Efeito fiscal dos itens identificados: quarterly Shell linha 45; subtrair o efeito assinado do total para obter imposto consolidado sem especiais.
- CCS: quarterly Shell linha 32. EBIT reconstruído já voltou à base histórica; não carregar imposto CCS como operacional nem aplicar ajuste em duplicidade.
- Juros após imposto: APM linhas 89/90 são LTM. A linha de receita é exclusivamente caixa/equivalentes segundo Annual Report 2025 p.435 PDF (433 impressa), enquanto receita de juros da DRE é total. Corrigir esse perímetro antes de inferir efeito fiscal. A diferença entre total de juros antes de imposto e caixa após imposto não é imposto das receitas financeiras.

Fórmula alvo: imposto operacional = imposto consolidado − imposto dos itens especiais − imposto das receitas financeiras + benefício fiscal das despesas financeiras, com mesma competência e perímetro do EBIT normalizado. Falta comprovar juros antes de imposto exclusivamente de caixa, impostos das demais receitas financeiras excluídas e abertura trimestral após imposto. Preservar ROCE indisponível; não usar NOPAT divulgado nem taxa fictícia.

Verificação dos componentes preparados, antes da revisão/publicação: FCO 2024 54.684; 2025 42.863. Distribuições/FCO 41,2662% e 52,1452%. Dívida líquida/EBITDA reconstruída 0,1452x e 0,3005x. CAPEX/FCO 35,8441% e 44,2060%, NÃO COMPARÁVEL. ROCE indisponível.


## Revisão metodológica posterior — NÃO publicar EBIT como comparável

As oito pontes anteriores são aritméticas; não comprovam a classificação econômica completa. A nota 9, p.270 PDF (268 impressa), contém juros, dividendos de títulos, ganhos/alienações, câmbio de financiamentos e outros. Dividendos de títulos: 2025 82 e 2024 83; câmbio de financiamentos: 2025 −537 e 2024 −1.025, USD milhões. Parte do câmbio 2024 (reclassificação de conversão) já aparece nos itens identificados; não excluí-la novamente. O remanescente financeiro precisa ser conciliado trimestralmente. "Other" contém sublease de joint operations (2025 420; 2024 493), de natureza operacional, além de outros valores: não excluir a linha inteira.

Por decisão do usuário, sem alternativa aprovada: gate explícito impede cálculo do EBITDA/EBIT candidatos para alavancagem e ROCE enquanto a revisão acima estiver pendente. Os números 0,1452x/0,3005x descritos anteriormente são cálculos candidatos, NÃO índices comparáveis aprovados. FCO e distribuições não dependem dessa revisão e seguem elegíveis.

ROCE: notas 7–10, reconciliações ROACE e releases trimestrais revistos não individualizam todos os efeitos fiscais dos resultados financeiros que devem sair do EBIT. Lucro operacional e imposto precisam ter os mesmos ajustes e perímetro. Corporate não pode ser eliminado inteiro (inclui custos operacionais). Nenhuma taxa, rateio anual ou NOPAT divulgado substitui a abertura rejeitada pelo usuário.

CAPEX: reconciliação de cash capital expenditure inclui DFC Capital expenditure, investimentos JV/associadas e títulos. Inorgânicos agregados não estão individualizados por essas três linhas: falta atribuição exata antes de excluir da base estatutária. Aplicar toda a soma à primeira linha poderia retirar aquisições já excluídas pelas duas últimas.

## Encerramento da pesquisa das pendências — critério estrito

Relatórios Q2 e Q4 de 2024 e 2025 acrescentados e preservados. Aberturas de câmbio de financiamentos e dividendos de títulos identificadas nos oito trimestres, com soma versus anual auditado conciliada em até USD 1 milhão. Evidências, hashes, páginas e verificações: `shell-pending-comparability-audit.json`. Isso resolve a ausência dos valores brutos trimestrais, mas não resolve seu efeito incremental sobre EBIT já ajustado, nem os impostos correspondentes.

As fontes examinadas compreendem databooks trimestral/anual, notas 7–10 do relatório anual e quatro releases semestrais/anuais que contêm oito trimestres. A abertura adicional não oferece os três vínculos necessários: (1) FX de financiamento antes/depois de retirar identified items no mesmo trimestre, incluindo composição de Other; (2) efeito fiscal de cada receita/despesa financeira no perímetro do EBIT; (3) inorgânicos por linha da DFC. Portanto não há base demonstrada nestas fontes para classificar ROCE/alavancagem/CAPEX como comparáveis. Não se afirma impossibilidade de divulgação futura ou inexistência universal de qualquer fonte. Permanecem bloqueados ROCE e alavancagem pela decisão do usuário; CAPEX permanece NÃO COMPARÁVEL. FCO e distribuições elegíveis não são bloqueados por essas lacunas.

Para habilitar pela regra estrita, é necessária nova abertura verificável dessas pontes, e não simplesmente aprovação dos números ou relaxamento de tolerância. Não ratear, inferir alíquota efetiva geral nem adotar numerador ROACE divulgado como substituto.


## Conclusão após revisão adicional das fontes de modelagem

Revisados também Financial Modelling Guidance (30/10/2025), suplemento Comparable GAAP measures and non-GAAP measures reconciliation e nota 23 de impostos (p.284 PDF, 282 impressa). O guia p.23 confirma que Corporate mistura funções administrativas, financiamento e seguros; não é um agregado financeiro removível integralmente. O suplemento não fornece a abertura fiscal ou os inorgânicos por linha que faltam.

A nota 23 abre ajustes legais (não dedutibilidade, incentivos, alienações, efeitos cambiais, diferenças de alíquota etc.), mas não a matriz entre essas categorias, itens financeiros e imposto operacional. Os totais de impostos e do resultado não determinam uma decomposição operacional única. O mesmo ocorre com inorgânicos: I = I_CAPEX + I_JV + I_títulos; a publicação do agregado I não determina I_CAPEX. Aplicar taxa média ou atribuir todo I à linha CAPEX seria nova premissa não aprovada.

Exceção demonstrável: Q3 2024 tem inorgânicos publicados zero. Suplemento `shell-2024q3-organic-capex.json` prepara CAPEX orgânico USD 4.690 milhões com guard que exige zero explícito e conciliação DFC/APM. Não habilita comparabilidade do LTM cujos outros trimestres continuam pendentes. Demais períodos: sem proxy, rateio ou estimativa.

Concluído: sob as regras estritas aprovadas e com as publicações examinadas, não há informação suficiente para tornar ROCE, alavancagem e CAPEX LTM comparáveis. Eles só poderão ser reclassificados mediante nova abertura verificável ou nova metodologia expressamente aprovada. Esta conclusão encerra a procura repetitiva nas mesmas publicações; não é alegação de impossibilidade universal nem autorização de alternativas rejeitadas.


## Decisão posterior: alternativas aprovadas pelo usuário

A aprovação posterior substitui a instrução de manter os índices indisponíveis até comparabilidade. Reconstrução estrita permanece não comprovada; alternativas numéricas ficam NÃO COMPARÁVEIS.

- ROCE: APM linha 91, numerador ajustado ROACE **já LTM**, dividido pela média dos capitais RADAR de abertura/fechamento, sem leases na base e caixa integral. Campo `nopat_ltm`, período `LTM`; usar apenas a referência final da janela, nunca somar quatro LTM ou inventar fluxos trimestrais. Ponte linha 88 + 89 + 90 (receita de juros já negativa). Não inferir imposto/EBIT.
- Alavancagem: APM linha 31, EBITDA ajustado divulgado, somado em quatro trimestres; dívida RADAR CP + LP − leases − caixa. Divulgação usa CCS e adiciona exploration well write-offs; NÃO COMPARÁVEL.
- Investimento orgânico ampliado/FCO: APM linha 50 menos inorgânicos linha 44. O agregado inclui investimentos em JV e títulos; subtrair inorgânicos do agregado completo evita escolher arbitrariamente uma linha. Ponte com três linhas DFC e inorgânicos. Sensibilidade de aportes JV indisponível nesta série para evitar dupla contagem.

Lotes consolidados de publicação em `shell-2024-publication.json` e `shell-2025-publication.json` substituem lotes v1/v2 e suplemento isolado Q3 2024. Contêm também FCO, distribuições, leases, goodwill e saldos de abertura. Não publicar os antigos após os consolidados.

Validação antes de publicação: ROCE 2024 12,9576%, 2025 10,7721%; alavancagem 0,1408x/0,2938x; investimento orgânico ampliado/FCO 37,1407%/44,5256%. As três alternativas classificadas NÃO COMPARÁVEIS. FCO e distribuições preservados.

Lotes finais consolidados, sem erros, componentes bloqueados ou conciliações reprovadas:

- 2024: `12739febc43f4a01b41670824c349411`.
- 2025: `a60858b98cf24447bd4fb547198ae131`.

Cada lote contém 59 componentes e 24 conciliações. Revisar/aprovar os campos elegíveis e publicar somente estes lotes; a metodologia aprovada não equivale à publicação automática.
