# ROCE sintético — regras v1.2.0

Autorizado pelo usuário em 05/10/2026. Dados e alíquotas são fictícios e não descrevem o regime fiscal ou os resultados das empresas.

- Chevron: 10%; Shell: 20%; Petrobras e Equinor: 25%.
- EBIT ajustado trimestral sintético = 65% do EBITDA sintético. A diferença representa DD&A fictício; itens especiais iguais a zero.
- Imposto operacional trimestral = EBIT ajustado × alíquota fictícia.
- NOPAT LTM = soma de EBIT ajustado menos imposto de quatro trimestres consecutivos.
- Capital empregado sintético = patrimônio líquido + NCI + dívida financeira − caixa não operacional, goodwill incluído. No gerador, PL+NCI inicial = oito vezes o FCO trimestral-base, crescendo 1,2% por período; dívida menos caixa usa a trajetória sintética já existente. Nenhum componente vem de fonte real.
- Capital empregado médio = (saldo no início da janela LTM + saldo no encerramento) / 2.
- ROCE percentual = NOPAT LTM / capital empregado médio × 100.
- Leases excluídos na base. Na sensibilidade, somados aos saldos inicial e final; NOPAT mantido. Não constitui reconstrução contábil real.
- Componentes ausentes/não finitos, janela incompleta/não consecutiva ou denominador zero: indisponível; não substituído por zero.

A visão reportada sintética permanece separada. O modelo persiste EBIT, imposto, alíquota, saldos inicial/final e leases iniciais com DECIMAL(28,6), exportados em CSV/Parquet. A migração adiciona uma revisão dos fatos demonstrativos existentes, preservando a versão anterior e documentos. Novas bases recebem os componentes diretamente; inicializações repetidas não duplicam revisões.

A hierarquia OPEN-03 continua aplicável aos dados reais. O cenário sintético é identificado como demonstração e não autoriza estimativas na visão padronizada real.
