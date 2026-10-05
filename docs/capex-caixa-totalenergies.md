# CAPEX consolidado de caixa — TotalEnergies 2025

Implementação de 05/10/2026, mapping `total-2025-cash-capex-v6`.

Base: pagamentos por imobilizado e intangíveis no perímetro consolidado. Aportes em afiliadas/JVs, aplicações financeiras e empréstimos ficam fora, conforme decisão aprovada. Não usar organic investments como substituto dessa linha.

Fonte: Accounts Q2/Q4, página 6, `Intangible assets and property, plant and equipment additions`. Sinal da saída invertido. Linha de referência anual: Accounts Q4, página 7; confirma o total da DFC do URD 2025, página 456.

| USD milhões | Q1 | Q2 | Q3 | Q4 | Ano |
|---|---:|---:|---:|---:|---:|
| Pagamentos por ativos | 4.222 | 4.766 | 3.812 | 4.153 | **16.953** |

Quatro trimestres conciliados com o anual, diferença zero. FCO anual 27.343; CAPEX/FCO = **62,001243%**; FCL = **10.390**.

A DFC identifica separadamente aquisições de subsidiárias, investimentos em afiliadas/títulos, empréstimos e alienações: essas linhas não entram na base. Não deduzir alienações do CAPEX bruto. A linha de caixa não equivale a adições contábeis de ativos: não adicionar ROU sem caixa, mudança de perímetro ou provisões de abandono. Exploração capitalizada não é adicionada novamente por fora. A base inclui desembolsos capitalizados classificados pela companhia nessa linha, não uma estimativa por variação do balanço.

Limite de classificação: a linha agregada não oferece decomposição trimestral por natureza de cada aquisição direta de ativo. Eventual aquisição de negócio classificada nessa linha exige exceção e ajuste documentado; não presumir que toda aquisição direta de ativo seja M&A. Classificar por natureza nas novas cargas. Esse perímetro de caixa consolidado deve ser aplicado consistentemente aos peers antes de afirmar comparabilidade entre empresas.

Referências públicas: [Accounts Q4](https://totalenergies.com/system/files/documents/totalenergies_accounts-q4-2025_2026_en.pdf), [Accounts Q2](https://totalenergies.com/system/files/documents/totalenergies_financial-statements-2Q25_2025_en.pdf), [URD 2025](https://totalenergies.com/system/files/documents/totalenergies_universal-registration-document-2025_2026_en.pdf).

Os antigos valores de organic investments ficam preservados como fatos de referência, sem campo CAPEX publicado. Lote `42a955e3fdc24a41a93c617135f11138` preparado em REVISAO no banco local, sem publicação automática. Teste de publicação realizado em cópia temporária: CAPEX/FCO comparável no controle interno, FCL e caixa residual calculados. 41 testes passaram. Sensibilidade com aportes em JVs continua indisponível até desagregação pública e conciliação.

## Sensibilidade de aportes em JVs implementada

Selecionar “Incluir aportes orgânicos em JVs” soma `jv_organic_contributions` ao CAPEX trimestral antes do LTM, alterando CAPEX/FCO, FCL e caixa residual. FCO, distribuições e ROCE não mudam. Campo de ingestão exige conceito `ORGANIC_JV_CASH_CONTRIBUTIONS`, basis RECONSTRUCTED, policy_note com classificação, valores não negativos, ponte de conciliação e aprovação. Quatro trimestres completos e perímetro compatível são obrigatórios; ausência não vira zero. Zero deve ser um fato documentado. A linha agregada “investments in equity affiliates and other securities” não é automaticamente elegível. O mapeamento da Total ainda não contém esses valores classificados; a opção permanece indisponível para esses dados. 42 testes passaram.
