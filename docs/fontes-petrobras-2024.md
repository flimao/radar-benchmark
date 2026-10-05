# Petrobras — carga de 2024

Carga preparada em 05/10/2026, regras v1.8.0, mapeamento
`petrobras-2024-common-basis-v1`. Lote `cfa6d1a038d64617a7e0c6b949c7a57c`
em REVISAO na Administração da Carga local (porta 8052).

## Fontes e controles

Central de resultados oficial Petrobras: quatro planilhas trimestrais em BRL
e quatro demonstrações financeiras consolidadas, incluindo anual auditada.
URLs, hashes SHA-256, seletores e verificações de rótulos/unidades/períodos
constam em `config/ingestion/petrobras-2024.json`. Os originais foram
preservados no diretório de dados da aplicação.

68 componentes, 21 conciliações, todas com diferença zero. Quatro pontes
de fluxos trimestrais com a DFC anual; cinco pontes de arrendamentos
CP + LP com total bruto BRL; quatro de EBIT; quatro de DD&A; quatro de
investidas líquidas com exclusão de sinal inverso na ponte EBITDA.

As linhas mudam entre publicações: Q1 usa Endividamento líquido e a ordem
de coparticipação/alienações difere. Não usar posições de linhas de 2025.
Traços nos ajustes de Q3 foram explicitamente tratados como zero.
Goodwill líquido foi extraído nas notas: Q1 p.31, Q2 p.34, Q3 p.38,
Q4 p.83; abertura 2023Q4 na nota anual.

## Metodologia aplicada

Fluxos BRL divididos pela média trimestral da PTAX venda Bacen antes
da soma LTM; saldos pelo fechamento, incluindo dezembro de 2023.
CAPEX: aquisições de imobilizado e intangível pagas, sem compensar
alienações; linha de investimentos em participações fica fora da base.
FCO estatutário; dividendos/JCP efetivamente pagos e recompras liquidadas.
Dívida financeira exclui leases; caixa integral conforme aproximação
aprovada. Leases e goodwill preservados para sensibilidades.

EBIT reconstruído mantém investidas líquidas e ajusta impairment,
alienações/baixas e coparticipação; DD&A conciliado separadamente.
Ajustes não abrangem automaticamente todos os eventos exclusivos.
Imposto normalizado = (EBIT ajustado - investidas líquidas) × 34%.
Não tributar novamente investidas; alternativa exclusiva Petrobras,
rotulada NÃO COMPARÁVEL. Não reproduz ROCE publicado pela companhia.

Resultados de validação antes de publicação, base sem leases:

| LTM | ROCE estimado |
|---|---:|
| 2024Q4 | 20,2481% |
| 2025Q1 | 17,9903% |
| 2025Q2 | 18,4230% |
| 2025Q3 | 16,8801% |
| 2025Q4 | 20,5601% |

2024: FCO US$ 37.912,426 mi; CAPEX/FCO 38,6322%; dívida
líquida/EBITDA 0,503086x. ROCE não comparável; sensibilidades de aportes
orgânicos JV continuam indisponíveis sem segregação documental.
O CAPEX de 2025 mantém a pendência de valor exato para Mero/Atapu.

Publicação financeira deve ocorrer pela Administração da Carga.
Nenhuma atualização da VPS foi realizada nesta etapa.
