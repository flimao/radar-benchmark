# Decisões para dados reais — 05/10/2026

## Aprovação recebida

Fonte cambial oficial: publicação do Banco Central do Brasil (Bacen), para uso consistente na normalização. OPEN-02: fonte, conversão BRL/USD e fluxos aprovados; saldos aprovados na atualização abaixo; demais moedas ainda pendentes. Não altera conversões já reportadas pelas empresas em USD, nem cria dados cambiais automaticamente.

Aprovado: PTAX venda de fechamento diário; fluxos BRL convertidos dividindo pela média aritmética das cotações R$/USD dos dias publicados no trimestre. Calcular trimestre na moeda original antes da conversão e somar trimestres convertidos para LTM. Valores originalmente reportados em USD permanecem reportados; reconstrução em USD via Bacen fica separada quando houver componentes e necessidade defensável.

Saldos aprovados: PTAX venda na data do balanço ou última publicação anterior. Permanece pendente o tratamento das outras moedas. Nenhuma taxa foi baixada nesta etapa.

## Políticas aprovadas pelo usuário

- Goodwill: manter incluído na base, conforme DRS. Sensibilidade excluindo goodwill dos saldos inicial/final, mantendo NOPAT; declarar quando for apenas sensibilidade de denominador.
- Híbridos: seguir classificação contábil divulgada na base, sem dupla contagem em PL/dívida; tratamento alternativo por instrumento apenas se material e documentado. Não presumir equivalência IFRS/US GAAP.
- Mapeamento: adapter por empresa/documento/período e normalização para conceitos comuns, preservando fatos, ajustes e locators.
- Integridade: hash, empresa, período, moeda, escala, locator e unicidade obrigatórios. Ausências bloqueiam o indicador afetado, não necessariamente todo o dataset.
- LTM: quatro trimestres consecutivos; ROCE também exige saldos inicial/final. Incompleto indisponível.
- Reconciliação: diferença absoluta menor ou igual ao maior de US$ 1 milhão ou 0,1% do total de referência, ou da tolerância calculada de arredondamento da fonte, se superior. Ajustes não se justificam apenas por estarem dentro da tolerância.
- Variação: superior a 30% em valor absoluto versus trimestre anterior gera alerta, com denominador anterior zero tratado separadamente; não bloqueia automaticamente.
- Comparabilidade: divergência conceitual sem reconstrução defensável torna a métrica não comparável, independentemente da reconciliação numérica. Preservar valor e motivo, com aviso NÃO COMPARÁVEL, fonte escura em negrito, fundo contrastante e borda. Excluir pontos da série regular e apresentar seus valores no alerta textual.
- Aprovação PoC: um responsável revisa mapeamento inicial por empresa/KPI e exceções; novos trimestres sem exceções podem seguir regras aprovadas, com publicação confirmada pelo responsável. Sem segregação obrigatória de funções.
- Estados: APROVADO (checks essenciais e revisão atendidos), ALERTA (anomalia justificada e aceita), REVISAO (pendência de análise), BLOQUEADO (integridade/cálculo inválido). Só APROVADO ou ALERTA aceito pode ser publicado para uso financeiro.

Limites e políticas aprovados para PoC; não equivalem a auditoria contábil. Regras v1.3.0. Avaliador de controles e visualização de não comparabilidade implementados; fluxo de aprovação e ingestão de fatos reais continuam pendentes.

Implementação: `radar.fx` converte BRL→USD e soma trimestres convertidos; `radar.quality` avalia controles, reconciliação, variação e elegibilidade. Avaliações de comparabilidade são versionadas em `metric_assessment` por empresa/período/KPI/visão. Dados sintéticos não foram marcados artificialmente como não comparáveis. Na versão 1.3.1, o seletor expõe as quatro combinações de leases e goodwill. O cenário sintético utiliza goodwill fictício de 10% do capital empregado, explicitamente documentado; valores reais continuam pendentes.

## Prazo, ambiente e empresas — atualização de 05/10/2026

- OPEN-01 aprovado: PoC em produção na VPS em 06/10/2026 às 10h (America/Sao_Paulo, UTC−03:00). Prazo registrado, implantação ainda pendente; não equivale a implantação realizada ou garantia de aceite integral.
- OPEN-04 resolvido: Ubuntu Server na última versão LTS, sem metas quantitativas de desempenho por ser PoC. Referência verificada: Ubuntu 26.04.1 LTS, https://releases.ubuntu.com/. Testes funcionais, segurança e persistência não foram dispensados.
- Seleção das empresas em aberto: Petrobras, TotalEnergies, Chevron e Shell são provisórias. OPEN-06 trata de cores, não da escolha das empresas; permanece pendente até definição do conjunto e aprovação do mapeamento.
- OPEN-02 continua parcialmente resolvida: saldo é uma posição em uma data (caixa, dívida, patrimônio, goodwill), diferente de fluxo acumulado no trimestre (FCO, CAPEX, EBIT). Para saldos, proposta ainda não aprovada: PTAX venda de fechamento da data do balanço, ou última publicação anterior quando não houver cotação. Fluxos continuam na média trimestral já aprovada.
- Para a implantação são necessários endereço/acesso da VPS, domínio e configuração de segredos. Não registrar credenciais neste documento.

## Saldos — aprovação de 05/10/2026

O usuário aprovou PTAX venda de fechamento na data do balanço, ou última cotação publicada anterior se não houver publicação nessa data. Converter BRL→USD por divisão. Registrar data do saldo, data efetiva da cotação, taxa e uso de publicação anterior. Ausência de cotação anterior mantém indisponibilidade, sem usar taxa futura. Implementado em `radar.fx`, regras v1.3.3. Coleta de taxas e integração com fatos reais continuam pendentes. Esta aprovação substitui a pendência de saldos registrada anteriormente; outras moedas continuam em aberto.

## Dimensionamento da VPS — aprovação de 05/10/2026

O usuário escolheu 2 vCPUs, 4 GB RAM e 80 GB SSD para poucos arquivos Excel/PDF e concorrência muito baixa. Ubuntu Server última LTS, conforme decisão anterior. Não há metas quantitativas de desempenho na PoC. Dimensionamento registrado; provisionamento, implantação e medição de responsividade continuam pendentes. Swap e limites de memória do DuckDB não foram aprovados nem configurados por esta decisão.
