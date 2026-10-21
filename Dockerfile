# Chopin's Streamlit app.
#
# Build:  docker build -t chopin .
# Run:    docker run --rm -p 8501:8501 --env-file <your env file> chopin
#
# Credentials are never baked into the image: they are expected at runtime, through
# `client_id`, `client_secret` and `refresh_token` environment variables.

# --- Builder: has uv, produces the virtualenv. Discarded afterwards. ---
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first, so this layer stays cached while pyproject.toml and uv.lock are untouched.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --extra app --frozen --no-install-project --no-editable

COPY chopin/ ./chopin/
RUN uv sync --extra app --frozen --no-editable

# --- Runtime: no uv, no build cache, only the virtualenv and the sources. ---
FROM python:3.13-slim

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY app/ ./app/
COPY confs/ ./confs/
COPY .streamlit/ ./.streamlit/

# Run unprivileged.
RUN useradd --create-home --uid 10001 chopin
USER chopin

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health')"

# `--server.address 0.0.0.0` only exposes the app inside the container network; restricting who can
# reach the published port is Tailscale's job.
CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
