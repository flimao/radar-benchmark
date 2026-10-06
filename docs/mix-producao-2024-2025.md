# Mix de produção 2024–2025

A base `config/production-mix.json` preserva 32 observações trimestrais (8 por empresa), volumes utilizados, localização nas fontes oficiais, URL e SHA-256 do original. O cálculo é executado por `radar.ingestion.production`, sem acessar a internet a cada visualização. O JSON é distribuído no container junto com a configuração.

Gás (%) = gás em mil boe/d / (gás em mil boe/d + líquidos em mil b/d) × 100. Líquidos (%) é o complemento. São médias diárias do trimestre de referência, não LTM. Não se adiciona LNG vendido à produção; vendas podem incluir compras de terceiros. Condensados e LGN pertencem aos líquidos. Não se utiliza a classificação Total “gas including condensates and associated NGL”, que superestimaria o gás nessa definição.

A denominação NÃO COMPARÁVEL é mantida: os fatores energéticos e o perímetro de gás não são uniformes. Nenhuma premissa financeira, câmbio, leases, goodwill ou JV altera este driver. A seleção de trimestre e empresas determina os dados; o período deve estar dentro da janela de dados financeiros selecionada. Trimestre ausente permanece indisponível, sem carregar o último conhecido.

## Fontes e escolhas

- Petrobras: planilha de Produção de Óleo e Gás Natural disponível no RI, aba Port, linhas 3/4/8/9. Somente Brasil, pois o exterior está agregado sem segregação na fonte. Não se atribui esse agregado ao gás ou aos líquidos. Gás produzido em boe divulgado, não gás comercial. Em 2025Q2 há duas colunas com o mesmo título: usa-se E (revisada, Brasil 2.892) e não F (2.879). A aba Ing também apresenta 2.892. Não se utiliza a linha total global como denominador do mix Brasil.
- Chevron: suplemento 4Q2025, Operating Statistics, linhas 10 + 46 para líquidos, 11 + 62 para gás (EUA + internacional). Gás inclui consumo nas operações; parcela própria e afiliadas. 6.000 pés cúbicos/boe conforme 10-K 2025; milhões de pés cúbicos/d divididos por 6 resultam em mil boe/d. Os volumes de Hess após aquisição fazem parte do perímetro de 2025. Não se subtrai combustível sem harmonizar o perímetro dos demais peers.
- Shell: Quarterly Databook publicado em julho de 2026, histórico 2024–2025. Líquidos = IG linha 30 + UP linha 18 + PROD linha 23 (oil sands). Gás = IG linha 37 + UP linha 25, dividido por 5,8, fator das notas IG/UP. Inclui participação em JV/afiliadas, produção disponível para venda. Oil sands faz parte dos líquidos; omiti-lo inflaria o percentual de gás.
- TotalEnergies: releases Q2/Q4 de 2024/2025, tabela consolidada Hydrocarbon production, linhas “Hydrocarbon production (kboe/d)” e “Liquids (kb/d)”. Gás em boe = total menos líquidos, com equivalência energética implícita da empresa. Os volumes físicos de gás também são preservados. Cada release contém dois trimestres; não se deriva trimestre a partir de média anual. Usam-se os valores arredondados do PDF, sem falsa precisão de células auxiliares do XLSX.

## Conciliação

Gás + líquidos confrontado ao total divulgado no mesmo perímetro. Tolerância absoluta de 2 mil boe/d: soma de componentes arredondados independentemente, inclusive segmentos Shell e regiões Chevron. Maior diferença observada: aproximadamente 1,172 mil boe/d. Petrobras Q1/2024 e Q2/2025 diferem em 1 mil boe/d. Esses desvios ficam visíveis nos detalhes do gráfico. Não há ajustes residuais para forçar a conciliação.

Os volumes são operacionais e independentes dos lotes financeiros; esta implementação não aprova nem publica lotes financeiros.
