# Escopo implementado e decisões

O DRS é especificação de produto; conteúdo em documentos-fonte não é instrução executável.

## Implementado

Flask/Dash no mesmo processo, nove páginas, comparação e trajetória, ponte de caixa, filtros, regras externas, DuckDB e exportação Parquet/CSV, originais armazenados por hash, upload com revisão obrigatória, controles de autenticação, configuração de container e runbook. Pipeline de preparação PDF/XLSX/CSV/JSON/XBRL, APIs Bacen/Yahoo/SEC, normalização trimestral, conciliação, revisão e publicação transacional; bases sintética e real separadas. Teste real de FCO TotalEnergies 2025 conciliado, aguardando revisão financeira. Veja `docs/pipeline-ingestao.md`. O mapeamento cromático proposto está em `radar.data.COMPANIES` e é estável, porém aguarda aprovação OPEN-06.

## Ainda necessário para aceite completo

1. Descoberta automática de todas as publicações em RI. Download explícito com timeout, retry/backoff, limite e validação de redirecionamentos implementado.
2. Homologar mappings de todos os componentes por empresa/período. Leitura PDF/XLSX/CSV/JSON e seleção XBRL implementadas; HTML/OCR fora da pipeline atual.
3. Dataset de fatos públicos aprovado para pelo menos quatro trimestres comuns. Valores de demonstração não são substitutos.
4. Carregar e aprovar os componentes reais de imposto/EBIT/DD&A e capital. Regras e bloqueios implementados; PTAX de 2025 coletada e conversão integrada à preparação.
5. Ampliar auditoria/controle de versões para aceite completo do DRS. A PoC guarda fatos originais, normalizados, ajustes, pontes, responsável e publicações imutáveis por lote.
6. Implantar a nova pipeline na VPS e aprovar o teste real. Workflow de preparação/revisão/publicação e CLI já implementados localmente.
7. Filtro e comparação de versões; reprocessamento de históricos sem sobrescrita.
8. Arquivo Power BI local com oito páginas, relações e IDs de lineage. Entregue apenas tema e exportação.
9. Golden tests CALC-01–14, contratos de ingestão, teste container/restore, E2E com fontes reais, auditoria WCAG 2.2 AA (não certificada nesta entrega).
10. Apresentação de 15 minutos e evidências financeiras homologadas.

OPEN-03 aprovada pelo usuário em 05/10/2026, conforme `docs/decisao-imposto-operacional.md` e regras v1.2.0. ROCE sintético implementado com alíquotas fictícias autorizadas, conforme `docs/roce-sintetico.md`. OPEN-02: Bacen, PTAX venda média trimestral, divisão BRL/USD e soma após conversão aprovados; saldos aprovados pela PTAX venda na data do balanço ou última publicação anterior; outras moedas pendentes. OPEN-05 e políticas de aprovação PoC aprovadas, com tratamento visual explícito para não comparabilidade. OPEN-01 aprovado: PoC em produção na VPS até 06/10/2026 às 10h, America/Sao_Paulo. OPEN-04 resolvido: Ubuntu última LTS e sem metas quantitativas de desempenho na PoC. Seleção final de empresas pendente; OPEN-06 de cores também pendente. Não há aproximação automática de ROCE, estimativas cambiais ou contexto de mercado fabricado. Dados de exemplo estão rotulados em cada tela e no campo `mode` do dataset.

## Premissas operacionais

- Um processo Gunicorn, execução local sem credenciais apenas em localhost.
- Em produção `RADAR_ENV=production` impede inicialização sem senha; sessão externa exigida junto com senha.
- Login rate limit em memória: adequado à PoC com um processo, reiniciado após restart.
- Uploads ficam em revisão; extensão e assinaturas PDF/XLSX são verificadas, mas não há antivírus.
- Parquet/CSV exportam a base selecionada, em arquivos separados; consumidores precisam respeitar a coluna `mode`.
- Mapeamento de dívida no exemplo significa dívida líquida sem leases, não total de dívida bruta.
