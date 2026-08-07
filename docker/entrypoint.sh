#!/usr/bin/env bash
# ===========================================================================
# Entrypoint da aplicação.
#
# O container só pode iniciar o pipeline depois que as dependências externas
# estiverem realmente prontas. O `depends_on: service_healthy` do Compose
# garante que o processo do Postgres subiu, mas não que a base já aceita
# conexões da aplicação nem que a tabela sensorsData existe com dados —
# e src/main.py falha imediatamente se ela estiver vazia (TrainService.train()
# precisa dos dados históricos).
#
# Ordem: Postgres pronto -> carga do CSV -> Ollama pronto -> pipeline.
# ===========================================================================
set -euo pipefail

log() { printf '\n[entrypoint] %s\n' "$*"; }

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
WAIT_TIMEOUT="${WAIT_TIMEOUT:-120}"

# ---------------------------------------------------------------------------
# 1. Aguarda o PostgreSQL aceitar conexões autenticadas
# ---------------------------------------------------------------------------
log "Aguardando PostgreSQL em ${DB_HOST}:${DB_PORT}..."
deadline=$(( SECONDS + WAIT_TIMEOUT ))
until python - <<'PY' 2>/dev/null
import os, sys, psycopg2
try:
    psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=os.environ["DB_NAME"],
        connect_timeout=3,
    ).close()
except Exception:
    sys.exit(1)
PY
do
    if (( SECONDS >= deadline )); then
        log "ERRO: PostgreSQL não respondeu em ${WAIT_TIMEOUT}s."
        exit 1
    fi
    sleep 2
done
log "PostgreSQL pronto."

# ---------------------------------------------------------------------------
# 2. Carga inicial dos dados de sensores
#
# sensor_service.importar_sensor_data() cria as tabelas e já é idempotente:
# se a tabela tiver qualquer linha, ele pula o import. Reexecutar é seguro.
# ---------------------------------------------------------------------------
if [ "${SKIP_DB_SEED:-0}" = "1" ]; then
    log "SKIP_DB_SEED=1 — carga inicial ignorada."
else
    log "Verificando carga inicial da tabela sensorsData..."
    python src/services/sensor_service.py

    # importar_sensor_data() trata suas próprias exceções e sai com código 0
    # mesmo quando o import falha. Sem esta verificação, o erro só apareceria
    # mais tarde, em df.iloc[-1] dentro do main.py, como um IndexError opaco.
    log "Confirmando que a tabela tem dados..."
    python - <<'PY'
import sys
sys.path.insert(0, "src")
from database.database import engine
from sqlalchemy import text

with engine.connect() as conexao:
    total = conexao.execute(text('SELECT COUNT(*) FROM "sensorsData"')).scalar_one()

print(f"[entrypoint] sensorsData: {total} registros.")
if total == 0:
    print(
        "[entrypoint] ERRO: a tabela está vazia. Verifique os logs da carga "
        "acima e se src/data/banner.csv foi copiado para a imagem.",
        file=sys.stderr,
    )
    sys.exit(1)
PY
fi

# ---------------------------------------------------------------------------
# 3. Aguarda o Ollama responder
# ---------------------------------------------------------------------------
log "Aguardando Ollama em ${OLLAMA_HOST}..."
deadline=$(( SECONDS + WAIT_TIMEOUT ))
until curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; do
    if (( SECONDS >= deadline )); then
        log "ERRO: Ollama não respondeu em ${WAIT_TIMEOUT}s."
        exit 1
    fi
    sleep 2
done
log "Ollama pronto."

# ---------------------------------------------------------------------------
# 4. Garante os modelos declarados em src/config/config.json
#
# Feito aqui, e não num serviço separado do compose, para que os nomes venham
# de uma única fonte de verdade — a mesma que main.py e chat_view.py leem.
# ---------------------------------------------------------------------------
if [ "${SKIP_MODEL_PULL:-0}" = "1" ]; then
    log "SKIP_MODEL_PULL=1 — download de modelos ignorado."
else
    python docker/ensure_models.py
fi

# ---------------------------------------------------------------------------
# 5. Executa o comando do container (CMD do Dockerfile)
#
# `exec` substitui o shell pelo processo Python, mantendo-o como filho direto
# do tini — sem isso, SIGTERM do `docker stop` não chegaria à aplicação.
# ---------------------------------------------------------------------------
log "Iniciando aplicação: $*"
exec "$@"
