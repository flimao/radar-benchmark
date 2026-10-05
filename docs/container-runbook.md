# Container local e VPS

Requisitos: Docker Engine/Desktop em execução e Docker Compose v2+.

No macOS, se Docker Desktop estiver instalado mas `docker` não estiver no PATH:

```bash
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

## Testes Linux/Python 3.12

```bash
docker compose -f compose.test.yaml build
docker compose -f compose.test.yaml run --rm tests
```

O estágio de teste não recebe segredos e usa dados temporários. O estágio production não inclui os testes nem pytest. requirements.txt fixa versões diretas; constraints.txt registra as versões transitivas do ambiente testado. A imagem-base usa uma tag, não digest imutável.

## Executar localmente

```bash
.venv/bin/python scripts/configure_container.py
docker compose up --build -d --wait
```

O script solicita a senha sem exibi-la, grava somente hash e segredo de sessão em `.env` com permissão 0600 e recusa sobrescrever um arquivo existente. `.env` fica fora do Git e da imagem. Aspas simples preservam `$` no hash.

Abra http://127.0.0.1:8051/login. Configure RADAR_PORT para outra porta se necessário. RADAR_HTTPS=0 somente para HTTP local. Não conflita com o Flask em 8050.

```bash
docker compose logs --tail=100 radar
.venv/bin/python scripts/check_container.py
```

A checagem solicita a senha, verifica /health, bloqueio anônimo, login e exportação. Recria o container e verifica persistência de um marcador de teste e da sessão. O marcador criado pelo teste é removido ao final; documentos e banco não são apagados.

Os dados do container ficam no volume `radar-data`, separados do banco local do repositório. Inicialmente são demonstrativos. `docker compose down` preserva o volume; **não usar `down -v`** se os dados precisarem ser conservados.

## VPS

Reconstruir a imagem na VPS Ubuntu com os mesmos arquivos (ou usar buildx linux/amd64 para uma VPS x86). Não copiar a imagem ARM do Mac diretamente para x86. Configure segredos na VPS e RADAR_HTTPS=1. Caddy/Nginx deve terminar HTTPS e encaminhar para 127.0.0.1:8051. Apenas o proxy recebe tráfego externo; o serviço web exige senha.

Executa com usuário UID/GID 10001, um worker Gunicorn e quatro threads, healthcheck e logs em stdout/stderr. O volume persistente contém banco, originais, curados e evidências. Backups consistentes exigem interromper escrita antes de copiar os dados. Processos de ingestão futuros devem coordenar acesso de escrita ao DuckDB.

## Evidência de verificação — 05/10/2026

Docker Desktop encontrado em `/Applications/Docker.app/Contents/Resources/bin/docker` (fora do PATH inicial). Imagens de teste e produção construídas em Linux ARM64/Python 3.12. 19 testes passaram dentro do container. `scripts/verify_container.py` confirmou inicialização production, health, rejeição de acesso anônimo/senha inválida, login válido, CSS, layout Dash, CSV com TotalEnergies e persistência de original/registro DuckDB após remoção e recriação do container com o mesmo volume. Credenciais aleatórias não foram exibidas; container e volume temporários de verificação foram removidos.

VPS x86/AMD64 ainda precisa de build e verificação no destino; implantação remota não realizada. Não há serviço de produção deixado em execução local: configure sua senha e execute Compose para iniciá-lo.

Para repetir a verificação descartável após construir `radar:local`:

```bash
.venv/bin/python scripts/verify_container.py
```

## Cadastro de trimestre

Em Administração da Carga, use Adicionar trimestre (exemplo: 2026Q1). O período é persistido no DuckDB do volume e aparece nos filtros e no upload. Cadastro repetido não duplica o registro; formatos inválidos são rejeitados. Nenhum fato financeiro é criado. Até a carga, indicadores trimestrais/TTM ficam indisponíveis; drivers não repetem o mix do último período disponível.

Após alterações no código, atualizar a imagem e o container com `docker compose up --build -d --wait`. O volume permanece preservado.

## Publicação v0 na VPS — 2026-10-05

URL: https://radar-benchmark.felipeloliveira.com.br. A v0 usa dados sintéticos.
Servidor acessível por `ssh radar-vps`, Ubuntu 24.04.5 LTS, x86_64,
2 vCPUs, 4 GB RAM e 80 GB SSD. Docker 29.1.3, Compose 2.40.3 e
Caddy foram instalados pelos repositórios Ubuntu. Código em `/opt/radar`.

Caddy (`/etc/caddy/Caddyfile`) termina HTTPS com certificado automático
renovável e encaminha para `127.0.0.1:8051`. O container não expõe a porta
8051 publicamente. Docker e Caddy iniciam com o sistema; o serviço RADAR
usa `restart: unless-stopped`. O volume `radar_radar-data` mantém o banco
 e arquivos enviados. Credenciais ficam em `/opt/radar/.env`, modo 0600,
com hash da senha, segredo de sessão e `RADAR_HTTPS=1`.

Validação: 20 testes passaram na imagem Linux/Python 3.12 da VPS;
container saudável; certificado validado pelo cliente HTTPS; redirecionamento
HTTP para HTTPS; bloqueio sem autenticação; login com cookie Secure;
páginas principais, layout Dash, CSS e exportação responderam HTTP 200.
A publicação inclui o cadastro de trimestre ainda não comitado.

Operação:

```bash
ssh radar-vps
cd /opt/radar
docker compose ps
docker compose logs --tail=100 radar
# Após enviar código atualizado:
docker compose up -d --build radar
```

Não usar `docker compose down -v`: isso remove os dados persistidos.
A senha compartilhada temporária foi entregue em arquivo local protegido,
fora do repositório; não incluir credenciais em commits.
