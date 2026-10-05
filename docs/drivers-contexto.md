# Drivers e contexto

A página apresenta Brent (US$/barril), câmbio (R$/US$), mix de produção gás/líquidos (% em boe) e margem de refino (US$/barril). Valores de `config/drivers-demo.json` são inteiramente fictícios; não são observações de mercado nem divulgações das empresas. O câmbio do gráfico não entra nos cálculos financeiros existentes e não se apresenta como PTAX efetivamente baixada.

O trimestre limita o histórico de linhas e define o recorte do mix. A seleção de empresas controla mix e refino; Brent e câmbio são comuns. Sensibilidades de leases/goodwill e visão financeira não alteram séries de contexto.

Brent de Eq. foi interpretado como Brent de equilíbrio (breakeven). Sem série homologada com definição comum, o painel mostra indisponibilidade. Não se estima automaticamente breakeven com FCO, dividendos ou CAPEX: é necessário documentar preço de gás, produção, escopo, despesas, impostos e distribuições considerados. Breakeven de projetos não substitui equilíbrio do caixa corporativo.

Fontes candidatas reais: Bacen PTAX, resultados/databooks oficiais de cada empresa e série pública de Brent a selecionar. Shell publica margem indicativa de refino, mas essa definição não é automaticamente equivalente às medidas das outras empresas. Dados reais precisam de fonte, período, locator e comparabilidade validados.

## Sobreposição de KPI

O seletor permite adicionar um dos cinco KPIs aos gráficos de Brent, câmbio e margem de refino. Driver no eixo esquerdo e linha contínua; KPI no eixo direito, linha tracejada e marcadores em losango, por empresa. A seleção persiste ao mudar filtros superiores. Visão reportada/padronizada e sensibilidades afetam o KPI, não o driver. Pontos não comparáveis são excluídos da série e preservados no alerta textual. Mix de produção permanece um gráfico de composição. Janelas LTM incompletas continuam como lacunas; não são zero. A sobreposição não demonstra correlação ou causalidade.
