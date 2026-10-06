# Margem indicativa de refino: benchmark comum

Implementado na branch ft/drivers, junto ao mix de produção real. É contexto comum às empresas selecionadas, não uma medida de margem realizada, lucro downstream ou eficiência relativa. Não se atribuem quatro margens empresariais ao mesmo preço de mercado.

## Fórmula

M_d = (2 × 42 × gasolina_d + 42 × diesel_d) / 3 − Brent_d.

Gasolina e diesel em US$/galão americano; 42 galões por barril. Brent em US$/barril. O resultado é US$/barril de matéria-prima do benchmark. Assume cesta fixa 2/3 gasolina, 1/3 diesel. A média trimestral é a média aritmética das margens diárias nas datas comuns às três séries, calculada antes de qualquer arredondamento. Preserva margens negativas.

## Fontes

Coleta direta da EIA, sem chave API, usando histórico HTML diário:

- RBRTED: Europe Brent Spot Price FOB, US$/barril.
- EER_EPMRU_PF4_RGC_DPGD: US Gulf Coast Conventional Gasoline Regular Spot Price FOB, US$/galão.
- EER_EPD2DXL0_PF4_RGC_DPGD: US Gulf Coast Ultra-Low Sulfur No 2 Diesel Spot Price, US$/galão.

URLs, unidades, títulos, instante de coleta, SHA-256 dos originais e observações diárias estão em `config/refining-market.json`. Os originais HTML são preservados em `RADAR_DATA_DIR/data/context/eia`. Não se usa Brent futuro Yahoo na fórmula: preços spot são mantidos em todas as pernas.

A cesta padronizada combina Brent europeu e produtos do Golfo dos EUA. É uma referência definida pelo RADAR, não a reprodução exata do benchmark EIA Gulf Coast com petróleo LLS. O benchmark exclui frete e diferenças geográficas, qualidade de óleo, custos operacionais, impostos, trading, hedge e rendimento real das refinarias. Usa uma referência comum com propósito de contexto, sem ranking das empresas.

Definição de crack spread: https://www.eia.gov/todayinenergy/includes/crackspread_explain.php

## Qualidade e período

A coleta deve cobrir todo o trimestre. Há pelo menos 40 observações comuns e cobertura mínima de 90% da união das datas com algum dos preços publicado. A cobertura não trata feriados como falha: mede a interseção sobre a união das séries. Datas sem uma das pernas são excluídas, sem forward fill ou interpolação. Trimestre com cobertura insuficiente fica indisponível. São controles de integridade da série de contexto, não a tolerância de conciliação financeira.

Snapshot inicial: 2024–2025, 507 preços Brent, 498 de gasolina e 498 de diesel. Todas as oito médias trimestrais passam o controle. A filtragem do gráfico usa o mesmo intervalo dos dados financeiros e permite sobrepor os KPIs no segundo eixo. A seleção de empresas altera os KPIs sobrepostos; o benchmark comum não muda.

## Atualização

No ambiente de desenvolvimento:

```sh
RADAR_DATA_DIR=/private/tmp/radar-ui-ingestion .venv/bin/python -m radar.ingestion.refining --start 2024-01-01 --end 2025-12-31
```

A coleta valida as três fontes e só então substitui o snapshot. Falhas preservam a versão anterior. O módulo usa httpx e bibliotecas padrão, já instalados; não adiciona dependências ao container. O snapshot é incluído na imagem pelo COPY config; atualizar uma imagem publicada exige reconstruí-la. Os originais preservados no volume são evidência, não leitura obrigatória do dashboard.

A extensão futura a referências regionais ponderadas por volumes exige fontes de preços e volumes de refino por região com cobertura compatível. Não se presume que o benchmark inicial corresponda ao perfil de cada companhia.
