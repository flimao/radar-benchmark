# Power BI local — preparação

Baixe `/export` na aplicação autenticada. O endpoint também gera `data/curated/facts.parquet` no volume configurado. Importe `facts.csv` usando Obter dados > Texto/CSV e importe `theme.json` como tema.

O campo `mode=DEMONSTRACAO` deve estar sempre visível. As séries não representam resultados reais. O arquivo PBIX final e métricas curadas com lineage ainda estão pendentes; não recalcular regras financeiras definitivas no DAX. Exportação atual é de fatos demonstrativos, não do dataset financeiro homologado.
