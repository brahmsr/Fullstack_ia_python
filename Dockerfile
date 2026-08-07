# syntax=docker/dockerfile:1.7

# ===========================================================================
# Manutenção Prescritiva — imagem da aplicação (pipeline + Streamlit)
#
# Build em dois estágios:
#   builder : compila/baixa as dependências dentro de um virtualenv isolado
#   runtime : imagem final, sem compiladores, rodando como usuário não-root
#
# O virtualenv é copiado inteiro entre os estágios. Isso mantém o gcc e os
# headers de desenvolvimento fora da imagem publicada (~600MB a menos) sem
# precisar reinstalar nada.
# ===========================================================================


# ---------------------------------------------------------------------------
# Estágio 1 — builder
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# build-essential/libpq-dev cobre caso algum pacote não ter wheel pronta para a plataforma e precisar compilar do fonte.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# Copiado sozinho, ANTES do código-fonte: a camada de dependências só é invalidada quando este arquivo muda. Editar src/ não refaz o pip install.
COPY requirements-docker.txt .

# O cache mount preserva os downloads do pip entre builds sem inflar a imagem final (o cache vive fora das camadas).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements-docker.txt


# ---------------------------------------------------------------------------
# Estágio 2 — runtime
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/app \
    # sem dispositivo de áudio no container: src/main.py pula a música de espera.
    APP_DISABLE_AUDIO=1 \
    # streamlit precisa ouvir em todas as interfaces e não tentar abrir browser.
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# libgomp1: runtime OpenMP exigido pelas wheels de xgboost e scikit-learn.
# libpq5: biblioteca cliente do PostgreSQL usada pelo psycopg2.
# curl: usado pelo HEALTHCHECK e pelo entrypoint
# tini: init mínimo (PID 1) que repassa sinais e recolhe processos zumbis.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libpq5 \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

# UID/GID fixos: garantem permissões previsíveis nos volumes montados.
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid 1001 --home-dir /app --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser docker/ensure_models.py ./docker/ensure_models.py
COPY --chown=appuser:appuser docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# O tema fica em $HOME/.streamlit (config global do Streamlit) em vez de ./.streamlit, porque main.py sobe o Streamlit com cwd=/app/src — a config de projeto não seria encontrada a partir dali.
COPY --chown=appuser:appuser .streamlit/ /app/.streamlit/

RUN chmod +x /usr/local/bin/entrypoint.sh && \
    mkdir -p /app/vectorstore && \
    chown -R appuser:appuser /app

USER 1001

EXPOSE 8501

# start-period generoso: antes do Streamlit subir, o main.py ainda carrega o vectorstore, valida o modelo e faz a primeira consulta ao RAG.
HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=5 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["python", "src/main.py"]
