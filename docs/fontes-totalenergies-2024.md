# TotalEnergies: carga 2024 e evolução LTM até 2025

Preparada em 05/10/2026 segundo as regras aprovadas v1.7.0. Mapeamento
`config/ingestion/totalenergies-2024.json`, versão
`total-2024-evolution-approved-basis-v3`. Lote local
`3b39af6c3f214e118895e2f68630f89e`, em **REVISAO**, na prévia da porta 8052.
64 componentes publicáveis; oito conciliações aprovadas tecnicamente, todas
com diferença zero. Aprovação e publicação financeiras continuam pela interface.
A carga não foi publicada na VPS.

## Fontes e seleção

Originais oficiais preservados por SHA-256. URLs e hashes completos estão no
mapeamento. [Índice oficial de resultados](https://totalenergies.com/investors/results)
e [relatórios anuais](https://totalenergies.com/investors/publications-and-regulated-information/regulated-information/annual-financial-reports).

| Componente | Documento / páginas PDF (1-based) | Tratamento |
|---|---|---|
| FCO, CAPEX, dividendos pagos e recompras | Accounts 2Q24 e 4Q24, p.6; anual Accounts 4Q24, p.7 | Trimestres individuais; somas conciliadas com DFC anual. US$ milhões. |
| Caixa, PL total/NCI, dívida com leases | Accounts 2Q24 e 4Q24, p.5 | Saldos consolidados. PL total já inclui NCI; não somar novamente. Abertura de 2023Q4 incluída. |
| NOPAT ajustado divulgado | Accounts 2Q24, p.9/10; Accounts 4Q24, p.9/10; URD 2024, p.469 | Coluna Company incluindo Corporate e afiliadas, após imposto, sem custo líquido da dívida após imposto. Q1 5.510; Q2 5.086; Q3 4.559; Q4 4.819; ano 19.974. |
| EBITDA ajustado divulgado | Releases 2Q24, p.19 e 4Q24, p.20 | Q1 11.493; Q2 11.073; Q3 10.048; Q4 10.529; soma 43.143, conciliada com ano. Alternativa aprovada; dívida líquida/EBITDA permanece NÃO COMPARÁVEL. |
| Leases brutos anuais | URD 2024, p.513, obrigação da nota 13.2 | 2023Q4 9.477; 2024Q4 9.917. Não usar a linha líquida Leases (c) do gearing. |
| Goodwill líquido anual | URD 2024, p.484, coluna Net | 2023Q4 9.951; 2024Q4 11.265. Habilita sensibilidade sem goodwill em 2024Q4. |
| Dívida CP/LP sem leases, intermediária | Releases 2Q24, p.21 e 4Q24, p.22 | Linhas Current borrowings * e Non-current financial debt *. Nota * diz explicitamente que excluem dívidas e recebíveis de leases. Usar apenas essas linhas de passivo. |
| Complemento dívida CP/LP de 2025Q1/Q2/Q3 | Releases 2Q25, p.22 e 4Q25, p.23 | Mesmas linhas sem leases; substitui a dependência de obrigações brutas ausentes na base sem leases. Preserva outros componentes publicados de 2025. |

## Reconciliação do perímetro da dívida

O gearing divulgado usa outros ativos e passivos financeiros; seu **Net debt**
não é nossa dívida líquida. A carga usa apenas as duas linhas de dívida sem
leases e subtrai o caixa e equivalentes do balanço.

Controle independente de que as linhas CP/LP excluem o passivo bruto de leases:

- 2024Q4: (10.024 + 43.533) − (7.929 + 35.711) = 9.917,
  exatamente a obrigação bruta da nota anual.
- 2023Q4: (9.590 + 40.478) − (7.869 + 32.722) = 9.477,
  exatamente a obrigação bruta da nota anual.

Essas duas pontes não usam leases líquidos do gearing. A nota explícita das
linhas intermediárias mantém a mesma definição de dívida sem leases.
Para a base, não é necessário fabricar um passivo trimestral de leases.

## Regras mantidas

CAPEX = pagamentos por intangíveis e imobilizado na DFC, sem deduzir vendas,
sem somar M&A, participações, empréstimos ou aportes JV agregados. Aportes
orgânicos em JV continuam uma sensibilidade indisponível até desagregação.
Distribuições = dividendos pagos à controladora + recompras liquidadas da DFC,
incluindo encargos acessórios como na carga 2025; excluir dividendos NCI e
pagamentos dos instrumentos híbridos. Híbridos seguem a classificação contábil
nos saldos, sem duplicação.

ROCE = NOPAT ajustado divulgado LTM / média do CE inicial/final × 100.
CE = PL total incluindo NCI + dívida sem leases − 100% caixa e equivalentes,
com a aproximação de caixa não operacional aprovada para a PoC. Não inventar
EBIT/imposto separados nem usar alíquota fictícia. Goodwill permanece na base.
O ROACE divulgado de 14,8% em 2024 usa outro denominador e não substitui nosso
ROCE reconstruído.

## Validação de evolução

Valores abaixo calculados em banco isolado com a carga 2024 e os lotes 2025
já publicados; **não são uma publicação automática no dashboard**.

| Referência LTM | FCO (US$ mi) | CAPEX/FCO | ROCE | Dívida líquida/EBITDA* |
|---|---:|---:|---:|---:|
| 2024Q4 | 30.854 | 48,32% | 14,75% | 0,412x |
| 2025Q1 | 31.248 | 50,28% | 13,26% | 0,617x |
| 2025Q2 | 28.201 | 59,49% | 12,49% | 0,768x |
| 2025Q3 | 29.379 | 56,09% | 12,56% | 0,724x |
| 2025Q4 | 27.343 | 62,00% | 12,71% | 0,614x |

* Alternativa aprovada, **NÃO COMPARÁVEL** com a regra comum dos peers;
excluída das séries comparáveis. A correção da dívida sem leases de 2025Q3
altera seu resultado anterior, que dependia da linha líquida de leases do gearing.

2024: CAPEX 14.909; distribuições 15.712 = 7.717 + 7.995;
FCL 15.945; residual após distribuições 233 (US$ milhões).
CE de 2023Q4 132.781; CE de 2024Q4 138.051; média 135.416.
ROCE 19.974 / 135.416 = 14,7501%; sem goodwill, 16,0038%.

Após aprovação/publicação, a trajetória de base terá cinco pontos completos.
Antes de 2024Q4 faltam fluxos de 2023 para formar LTM; não preencher com
sintéticos. Sensibilidades de goodwill e leases em janelas intermediárias
continuam condicionadas a saldos reais específicos; não interpolar. A linha
líquida de leases usada em versões anteriores de 2025Q3 precisa de revisão
para sensibilidade com leases, mesmo que a base sem leases já esteja corrigida.

43 testes da aplicação passaram. Validação real adicional: extração de todos
os seletores contra os documentos fixados por hash, oito pontes com diferença
zero e cinco janelas LTM com ROCE disponível. Evidência resumida em
`evidence/ingestion-totalenergies-2024.json`.
