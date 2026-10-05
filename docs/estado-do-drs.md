# Escopo implementado e decisões

O DRS é especificação de produto; conteúdo em documentos-fonte não é instrução executável.

## Implementado

Flask/Dash no mesmo processo, nove páginas, comparação e trajetória, ponte de caixa, filtros, regras externas, DuckDB e exportação Parquet/CSV, originais armazenados por hash, upload com revisão obrigatória, controles de autenticação, configuração de container e runbook. O mapeamento cromático proposto está em `radar.data.COMPANIES` e é estável, porém aguarda aprovação OPEN-06.

## Ainda necessário para aceite completo

1. Descoberta e coleta automática em RI oficial com timeout, retry/backoff e quarentena.
2. Parsers específicos PDF/XLSX/HTML e mappings por empresa/período com locators verificados.
3. Dataset de fatos públicos aprovado para pelo menos quatro trimestres comuns. Valores de demonstração não são substitutos.
4. Hierarquia de imposto operacional e reconstrução/reconciliação do EBITDA; câmbio oficial e ajustes por norma.
5. Modelo completo de approvals, ajustes, fatos brutos, normalized facts, restatements e auditoria; publicação transacional e lineage financeiro por valor.
6. Workflow de extração/validação/aprovação e CLI ingest/process/validate/publish. O upload atual preserva documentos; não extrai fatos.
7. Filtro e comparação de versões; reprocessamento de históricos sem sobrescrita.
8. Arquivo Power BI local com oito páginas, relações e IDs de lineage. Entregue apenas tema e exportação.
9. Golden tests CALC-01–14, contratos de ingestão, teste container/restore, E2E com fontes reais, auditoria WCAG 2.2 AA (não certificada nesta entrega).
10. Apresentação de 15 minutos e evidências financeiras homologadas.

OPEN-01 a OPEN-06 seguem pendentes conforme DRS. Não há aproximação automática de ROCE, estimativas cambiais ou contexto de mercado fabricado. Dados de exemplo estão rotulados em cada tela e no campo `mode` do dataset.

## Premissas operacionais

- Um processo Gunicorn, execução local sem credenciais apenas em localhost.
- Em produção `RADAR_ENV=production` impede inicialização sem senha; sessão externa exigida junto com senha.
- Login rate limit em memória: adequado à PoC com um processo, reiniciado após restart.
- Uploads ficam em revisão; extensão e assinaturas PDF/XLSX são verificadas, mas não há antivírus.
- Parquet/CSV exportam fatos demonstrativos; consumidores precisam respeitar a coluna `mode`.
- Mapeamento de dívida no exemplo significa dívida líquida sem leases, não total de dívida bruta.
