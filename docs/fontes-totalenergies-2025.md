# Mapa de fontes — TotalEnergies, 2025

Mapeamento documental em 05/10/2026. Esta etapa identifica fontes e transformações; não aprova nem publica novos valores financeiros. A configuração executável v2 carrega FCO, distribuições, saldos e referências não comparáveis de investimento. As reconstruções abaixo ainda não estão implementadas.

## Fontes oficiais e cobertura

- [Resultados e documentos por trimestre](https://totalenergies.com/investors/results).
- [Accounts 4Q25](https://totalenergies.com/system/files/documents/totalenergies_accounts-q4-2025_2026_en.pdf): balanços de dezembro/setembro de 2025 e dezembro de 2024; DFC trimestral Q4/Q3 e anual.
- [Accounts 2Q25](https://totalenergies.com/system/files/documents/totalenergies_financial-statements-2Q25_2025_en.pdf): balanços de junho/março; DFC trimestral Q2/Q1 e semestral.
- [Databook 4Q25](https://totalenergies.com/system/files/documents/totalenergies_databook-q4-2025_2026_en.xlsx): componentes e conciliações das medidas alternativas; Q4, Q3 e ano. Q1/Q2 precisam dos respectivos databooks da página oficial; não dividir o anual por quatro.
- [Release 4Q25](https://totalenergies.com/system/files/documents/totalenergies_pr-results-q4-2025_2026_en.pdf): glossário e conciliações §§10.1–10.7, páginas 20–25; informações por segmento e apêndices.
- [Relatório semestral 2025](https://totalenergies.com/sites/g/files/nytnzq121/files/documents/totalenergies_half-year-financial-report_2025_en.pdf) e [Notas 3Q25](https://totalenergies.com/system/files/documents/totalenergies_3q25-notes_2025_en.pdf): complementam classificações e operações. Para goodwill de abertura/fechamento, buscar também as notas anuais 2024/2025; goodwill de uma aquisição não é o saldo consolidado.

Moeda de apresentação: USD; escala financeira: milhões. Valores de balanço são saldos; DFC trimestral já apresenta fluxos do trimestre. Valores anuais servem para conciliação. TotalEnergies segue IFRS; não aplicar os atalhos dos dados sintéticos.

## Mapeamento por indicador

| Indicador RADAR | Fonte e componentes | Transformação e pendência |
|---|---|---|
| FCO | Accounts Q4/Q2, p.6, cash flow from operating activities | Já mapeado: quatro trimestres somam 27.343. CFFO sem capital de giro e DACF são medidas diferentes. |
| Distribuições/FCO | DFC, p.6: dividendos pagos aos acionistas da controladora + compras de ações próprias | Inverter sinal das saídas. Separar dividendos de minoritários, cupons e resgate de perpétuos. Conciliar DFC anual; §10.7 é referência adicional com diferença de taxas nas recompras. |
| CAPEX/FCO | DFC de investimento + ponte §10.3; aquisição de imobilizado/intangível, exploração capitalizada e investimentos orgânicos em afiliadas | Reconstruir desembolso orgânico em caixa, excluindo M&A, alienações, investimentos financeiros e itens sem caixa. Organic investments não entra automaticamente como CAPEX. |
| FCL | FCO − CAPEX normalizado | Calculável após a ponte de CAPEX. Não usar o free cash flow divulgado: ele parte do CFFO sem capital de giro. |
| Caixa residual | FCL − distribuições | Depende do CAPEX e das distribuições normalizados. |
| Dívida líquida/EBITDA | Balanço p.5; databook §10.5 para dívida sem leases; §§10.2.1/10.2.2 para EBITDA/DDA | Reconstruir dívida da base e EBITDA com perímetro operacional e ajustes compatíveis. Não importar gearing nem net debt publicados como se fossem conceitos RADAR. |
| ROCE | EBIT ajustado, imposto operacional compatível e capital empregado de abertura/fechamento | Ponte fiscal ainda necessária; ROACE reportado usa definição própria e fica separado do cálculo RADAR. |

## Locators verificados e pontos de conciliação

### Distribuições

Accounts Q2 e Q4, p.6: o rótulo Parent company shareholders aparece em emissões e em dividendos. O seletor deve usar a ocorrência de dividendos, conferindo visualmente o bloco. Treasury shares é saída de caixa, diferente do anúncio de recompra.

Valores trimestrais de dividendos da controladora: Q1 1.851; Q2 1.894; Q3 2.216; Q4 2.160; total 8.121. Compras de ações próprias na DFC: 2.152; 1.707; 2.349; 1.506; total 7.714. A referência §10.7 soma 7.496, excluindo taxas e impostos. Registrar a diferença de 218, sem forçar igualdade entre definições. A escolha de incluir despesas acessórias deve aparecer no mapeamento da distribuição de caixa.

### Dívida, caixa, patrimônio e leases

Accounts p.5 fornece patrimônio da controladora, minoritários, dívida corrente/não corrente e caixa. Patrimônio total já inclui minoritários: usar total OU controladora + minoritários.

Databook §10.5, colunas C/D/E: fechamento 2025Q4/2025Q3/2024Q4. Linhas 3 e 7 trazem dívida corrente/não corrente excluindo leases; linha 9, caixa; linhas 12–14, patrimônio; linha 18, leases. Usar guards de datas e rótulos e manter os valores completos do XLSX, arredondando só na tela.

O net debt divulgado também inclui outros ativos/passivos financeiros e saldos classificados para venda. A base RADAR subtrai caixa da dívida financeira; a divergência deve ser explicada por componentes, não resolvida copiando o total divulgado. Para Q1/Q2, extrair os mesmos conceitos dos databooks correspondentes. Verificar classificação dos híbridos em cada saldo: mantê-los conforme contabilidade, sem adicionar de novo ao endividamento.

### EBITDA e EBIT

Databook §10.2.1: EBITDA em B13/C13/G13 (Q4/Q3/ano); DDA ajustado = linhas 9 + 10. §10.2.2 fornece ponte independente por componentes.

A ponte inclui resultado de afiliadas e outros resultados financeiros. EBITDA divulgado menos DDA produz um resultado antes do custo da dívida líquida com esse perímetro; não basta chamá-lo de EBIT operacional RADAR. Identificar quais componentes financeiros são operacionais, retirar os demais e documentar a mesma adjustment_set em EBIT e DDA. DDA da DFC contém impairments reportados e não substitui DDA ajustado.

### CAPEX

Databook §10.3 contém ponte de investimento estatutário para medidas da companhia. Linhas 7, 13, 16–18 revelam leasing capitalizado, financiamento/ganhos de projetos renováveis e empréstimos, exigindo tratamento explícito. Não subtrair todas essas linhas mecanicamente: distinguir financiamento de projeto, aporte orgânico em afiliada e aplicação financeira. Guardar os componentes como observações e conciliar com a DFC. Enquanto não houver reconstrução defensável, investimento publicado é referência não comparável, e FCL/caixa residual continuam indisponíveis.

### Imposto, capital empregado e goodwill

Imposto total ajustado em §10.2.1, linha 8, ainda inclui o perímetro do resultado financeiro. Informações por segmento trazem imposto sobre resultado operacional, mas os ajustes também possuem efeitos fiscais: comprovar compatibilidade antes de usá-lo contra EBIT ajustado. Preferir imposto operacional divulgado compatível; caso contrário, reconstrução documentada. Não usar imposto pago, taxa efetiva global ou alíquota fictícia de 25%.

§10.6 traz capital empregado e ROACE da companhia como referências. Reconstruir CE RADAR a partir de patrimônio + dívida financeira sem leases − caixa não operacional, com política de caixa documentada. ROCE LTM de Q4/2025 exige saldo 2024Q4, além de 2025Q4. Leases devem estar disponíveis nos dois extremos para a sensibilidade. Goodwill exige saldo específico nas notas nos dois extremos; intangíveis totais e goodwill adquirido no ano não servem como substitutos.

## Sequência de implementação

1. Acrescentar dividendos/recompras e conciliar as quatro DFCs com o ano; registrar a diferença de taxas do payout publicado.
2. Acrescentar dívida, caixa, patrimônio e leases com definições consistentes nos cinco fechamentos, incluindo abertura.
3. Reconstruir CAPEX com a ponte de investimento e liberar FCL, caixa residual e CAPEX/FCO quando revisados.
4. Normalizar EBIT/DDA e ponte fiscal para liberar alavancagem e ROCE; obter goodwill específico para a sensibilidade.

Cada etapa gera lote para revisão, com URL, hash, página/célula, período, conceito, ajustes e conciliação. Fonte encontrada não significa valor aprovado. Yahoo Finance pode servir como confronto/contexto, mas não substitui as notas oficiais para resolver diferenças de reporting.

## Complemento: plano para habilitar CAPEX e ROCE

Escopo inicial: LTM terminado em 2025Q4. São necessários quatro fluxos trimestrais de 2025 e, para ROCE, apenas os saldos de 2024Q4 e 2025Q4. Saldos intermediários são necessários para outros trimestres de referência, não para esse denominador LTM.

### Cobertura adicional encontrada

[Release 2Q25](https://totalenergies.com/system/files/documents/totalenergies_2Q25-results-press-release_2025_en.pdf): §§10.2 e 10.3 cobrem Q2/Q1 e semestre; §10.5, página 22, traz leases de junho e março. O release é alternativa de extração aos respectivos databooks; o semestre serve como controle independente. [Release 1Q25](https://totalenergies.com/system/files/documents/totalenergies_1q25-results-press-release_2025.pdf) permite confronto de Q1. Verificar os seletores ao extrair; layouts não são intercambiáveis automaticamente.

### CAPEX: componentes a extrair e classificar

| Componente | Fonte | Destino proposto |
|---|---|---|
| Pagamentos por imobilizado/intangíveis | Accounts Q2/Q4, p.6, bloco de investimento | Ponto de partida de caixa consolidado; verificar exploração capitalizada já incluída para não contar duas vezes. |
| Aquisições de subsidiárias e participações | Mesma DFC; notas de combinações de negócios | Excluir M&A; separar aquisição de participação de aporte para construção orgânica. |
| Investimentos em afiliadas e outros títulos | Mesma DFC e notas por operação | Desagregar: aporte orgânico de JV identificado separadamente; títulos/aplicações financeiras excluídos. A linha agregada não prova CAPEX. |
| Empréstimos concedidos/recebidos | DFC e §10.3 | Separar financiamento de desenvolvimento de projeto de aplicação financeira; não presumir inclusão pelo rótulo organic. |
| Leasing capitalizado | §10.3 | Separar adição de ROU sem caixa de pagamentos efetivos; excluir adição sem pagamento da base CAPEX. Não deduzir o valor inteiro sem conferir a natureza. |
| Venda e financiamento de renováveis | §10.3 e apêndice por segmento | Explicar efeitos de alienações, ganho e dívida de parceiros; remover itens sem desembolso orgânico e preservar perímetro consolidado. |
| Carbon credits e exploração | §10.3, notas de intangíveis/exploração | Verificar capitalização e caixa; não duplicar valores já presentes na primeira linha. |

Ponte proposta: CAPEX de caixa consolidado = pagamentos orgânicos por ativos + demais desembolsos orgânicos identificados − parcelas financeiras/M&A/não caixa incluídas nas linhas de origem. Aportes orgânicos em JV devem ter subtotal separado e política explícita de inclusão no KPI. Não usar total de investimento líquido de alienações. Conciliar cada ajuste com a DFC e explicar a diferença para organic investments divulgado. Se a desagregação pública não existir, o componente afetado permanece não comparável: isso é falta de evidência, não uma aprovação pendente.

Critério de liberação: quatro valores trimestrais no mesmo perímetro, ponte de caixa rastreável, soma anual conciliada e revisão das classificações. Isso também libera FCL e caixa residual.

### ROCE: mapa do numerador

| Campo | Fonte candidata | Evidência ainda necessária |
|---|---|---|
| EBIT ajustado | §§10.2.1/10.2.2 dos releases/databooks Q2/Q4 | Partir da ponte ajustada antes de DDA/custo da dívida; classificar outros resultados financeiros e afiliadas. Registrar cada retirada e incluir Corporate/eliminações. |
| DDA ajustado | §10.2.1, componentes tangíveis e intangíveis | Mesmo conjunto de ajustes do EBIT; exigido para EBITDA e controle da ponte, não diretamente na fórmula ROCE. |
| Imposto operacional | Informação por segmento, linha de imposto operacional; notas fiscais e ajustes | Ponte dos impostos correntes/diferidos que retire resultado financeiro/não operacional e acompanhe ajustes especiais do EBIT. A linha de imposto por segmento e o resultado operacional ajustado não são automaticamente compatíveis. |
| NOPAT | EBIT ajustado − imposto operacional compatível | Conciliar com resultado operacional após imposto no mesmo perímetro; valores de ROACE divulgado são controle, não substituição. |

Os ajustes de resultado apresentados líquidos de imposto não permitem recuperar separadamente EBIT e imposto sem outra evidência. Usar taxa efetiva arredondada para inferir imposto também não atende à hierarquia aprovada. Caso as notas não desagreguem efeitos fiscais suficientes, ROCE padronizado permanece não comparável. Uma estimativa fiscal só pode ser apresentada como sensibilidade explícita, jamais como base real aprovada.

### ROCE: mapa do denominador

CE = patrimônio total (incluindo NCI uma vez) + dívida financeira sem leases − caixa não operacional. Usar média simples dos dois extremos.

- Patrimônio: Accounts p.5, abertura 2024Q4 e fechamento 2025Q4, já extraídos.
- Dívida: confrontar dívida contábil com §10.5, que exclui tanto recebíveis quanto dívidas de leasing. A diferença entre balanço e quadro de gearing não pode ser atribuída integralmente a leases: outros componentes/classificações podem divergir. Abrir CP/LP e conciliar; manter híbridos conforme classificação contábil.
- Caixa não operacional: saldo de cash and cash equivalents é conhecido, mas falta identificar parcela restrita/operacional nas notas. Usar 100% do caixa como não operacional seria uma premissa adicional, a validar explicitamente, e não um fato divulgado.
- Sensibilidade leases: saldos dos dois extremos estão em §10.5. Não altera automaticamente EBIT/imposto.
- Sensibilidade goodwill: obter saldo consolidado específico nos dois extremos em notas anuais; não é requisito do ROCE base.

### O que exige decisão do responsável

1. Perímetro de aportes orgânicos em JV no CAPEX, mantendo subtotal separado.
2. Classificação de outros resultados financeiros/afiliadas no EBIT, coerente com o capital investido correspondente.
3. Política para caixa não operacional quando as notas não permitirem separar caixa necessário à operação.

Essas decisões precisam de valores/operacões concretos para revisão. A hierarquia do imposto, a exclusão de itens sem caixa/M&A e o tratamento contábil de híbridos já foram aprovados e não exigem nova autorização. Primeiro extrair e apresentar as pontes; depois revisar classificações e publicar. Aprovação não supre componente ausente.
