# Fontes de EBITDA — TotalEnergies 2025

Verificação em 05/10/2026. Há cobertura oficial dos quatro trimestres, DDA ajustado e duas pontes de conciliação. Esta etapa documenta fontes; não publica nem habilita automaticamente EBITDA padronizado.

## Fontes e locators

- [Release 2Q25](https://totalenergies.com/system/files/documents/totalenergies_2Q25-results-press-release_2025_en.pdf), página 20, §10.2.1: Q2, Q1 e semestre; §10.2.2 na mesma página: ponte a partir das receitas.
- [Release 4Q25](https://totalenergies.com/system/files/documents/totalenergies_pr-results-q4-2025_2026_en.pdf), página 21, §10.2.1: Q4, Q3 e ano; §10.2.2: ponte a partir das receitas.
- [Databook 4Q25](https://totalenergies.com/system/files/documents/totalenergies_databook-q4-2025_2026_en.xlsx), §10.2.1, B/C/G: Q4/Q3/ano. EBITDA linha 13, DDA tangível linha 9, amortização intangível linha 10. §10.2.2 apresenta confronto por componentes.
- [URD 2025](https://totalenergies.com/system/files/documents/totalenergies_universal-registration-document-2025_2026_en.pdf), nota 6.2, página 480: classificação anual de outros resultados financeiros. Não usar essa abertura anual como se fosse trimestral ajustada.

## Valores identificados (USD milhões)

| Componente | Q1 | Q2 | Q3 | Q4 | Ano |
|---|---:|---:|---:|---:|---:|
| EBITDA ajustado divulgado | 10.504 | 9.690 | 10.295 | 10.066 | **40.555** |
| DDA tangível ajustado | 2.998 | 3.106 | 3.277 | 3.184 | **12.565** |
| Amortização intangível ajustada | 83 | 96 | 104 | 99 | **382** |
| EBITDA menos DDA (candidato a EBIT) | 7.423 | 6.488 | 6.914 | 6.783 | **27.608** |

Somas trimestrais conferidas: EBITDA do semestre 20.194 e anual 40.555; DDA combinado anual 12.947. A soma não prova, sozinha, compatibilidade de perímetro entre empresas.

## Duas pontes disponíveis

1. §10.2.1: lucro ajustado da controladora + NCI ajustado + imposto ajustado + DDA ajustado + juros da dívida − rendimento líquido de caixa = EBITDA divulgado. Os juros/rendimento de caixa são retirados; não reconstruir via NOPAT aprovado, que tem outro perímetro de impostos/ajustes.
2. §10.2.2: receitas + compras/variação de estoque + outras despesas operacionais + exploração + outros resultados + outros resultados financeiros + resultado de afiliadas = EBITDA divulgado. Usar sinais publicados e controlar duplicidade de rótulos no PDF.

## Compatibilidade com a base RADAR

EBITDA divulgado é uma fonte completa e conciliável; EBITDA RADAR continua definido como EBIT ajustado normalizado + DDA do mesmo conjunto de ajustes. A ponte publicada mantém outros resultados financeiros e contribuição de afiliadas. Afiliadas devem ser mantidas coerentes com o capital, conforme decisão aprovada.

A nota 6.2 separa, no resultado financeiro reportado anual, dividendos de participações, juros capitalizados, atualização de obrigações de abandono e outros itens. Portanto, excluir toda a rubrica indiscriminadamente seria incorreto. É necessário classificar o conteúdo ajustado/trimestral antes de afirmar plena comparabilidade do EBITDA divulgado com o EBITDA comum dos peers.

Próxima implementação possível: carregar EBITDA divulgado com suas duas pontes e soma anual como referência rastreável; normalizar somente ajustes de financiamento comprovados. Uma alternativa documentada que aceite o perímetro do EBITDA divulgado precisa de decisão explícita, em vez de etiquetá-lo silenciosamente como EBITDA padronizado.

Para dimensionar a alternativa: dívida financeira sem leases ao final de 2025 = 48.995 + 12.038 − 9.927 = 51.106; menos caixa 26.202 = dívida líquida 24.904. Dividir pelo EBITDA divulgado 40.555 produz **0,61407x**. Valor diagnóstico, não publicado nem homologado como indicador comparável entre peers.


## Verificação de compatibilidade com a regra aprovada

Conclusão: compatibilidade parcial; a igualdade EBITDA = EBIT + DDA é reconstruível, mas o EBIT candidato ainda contém itens de financiamento e rubricas de natureza não segregada.

| Requisito | Evidência | Resultado |
|---|---|---|
| Quatro trimestres e soma anual | Releases Q2/Q4, §10.2 | Atendido: 40.555 |
| DDA e resultado com mesmos ajustes | Duas pontes §10.2 | Atendido dentro da definição divulgada: DDA 12.947 |
| Retirar juros da dívida e rendimento do caixa | §10.2.1 | Atendido para as linhas explícitas |
| Preservar afiliadas coerentes com capital | §10.2.2 inclui 2.848 de afiliadas ajustadas | Compatível com política aprovada; contribuição permanece líquida de imposto/DDA próprios |
| Excluir demais resultados de financiamento | Nota 6.2 versus §10.2.2 | Não comprovado integralmente |

A nota 6.2 (URD p.480) identifica juros capitalizados de 624 no resultado financeiro reportado anual. Essa é uma linha ligada a financiamento; sua manutenção exige reconciliação com a definição operacional aprovada, incluindo a contabilização da despesa financeira de contrapartida. Não subtrair 624 automaticamente: primeiro verificar se o componente permanece por inteiro no valor ajustado e se retirá-lo não duplica exclusão já feita pela ponte.

Também há dividendos de participações não consolidadas 205 e atualização das obrigações de abandono 589, além de outras receitas 608 e despesas 292. Dividendos precisam ser coerentes com o investimento no capital; atualização de abandono decorre da operação, embora classificada financeiramente. Os totais reportados não substituem os totais ajustados: outras receitas financeiras passam de 1.437 reportadas para 1.339 ajustadas; outras despesas são 881 em ambos. Falta abertura dos 98 de ajustes e dos componentes trimestrais de cada rubrica.

Portanto não homologar automaticamente 40.555 como EBITDA normalizado. Há uma medida divulgada conciliada, apta a alternativa explicitamente identificada; usar essa alternativa para alavancagem exige aprovação específica do perímetro, pois a aprovação do NOPAT para ROCE não autoriza automaticamente mudança na definição EBITDA.

## Alternativa aprovada e implementada

Usuário aprovou nesta conversa em 05/10/2026. Regra v1.7.0: TotalEnergies pode usar EBITDA ajustado divulgado como alternativa documentada na alavancagem, caso EBITDA normalizado não esteja disponível. O valor é calculado, mas recebe NÃO COMPARÁVEL e motivo explícito, pois a aprovação da alternativa não comprova equivalência de perímetro com peers. A série comparável continua excluindo o ponto. Outros peers não recebem automaticamente essa autorização. Sem quatro trimestres conciliados/publicados, permanece indisponível.

Lote local preparado `6e7e169dae5443f8a495380a6d885ce4`, REVISAO. Conferência em cópia temporária: 0,6140796449x, com status NAO_COMPARAVEL por método alternativo. Não publicado automaticamente. 42 testes passaram. O campo EBIT não foi preenchido por diferença para viabilizar essa alternativa.
