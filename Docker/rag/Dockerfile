FROM astral/uv:python3.11-alpine

WORKDIR /app
RUN apk add --no-cache \
    libpq \
    libpq-dev \
    gcc \
    musl-dev
    
COPY src/pyproject.toml src/uv.lock ./
RUN uv sync --locked --no-install-project

COPY src/ ./
COPY Docker/rag/alembic.ini ./database/alembic.ini

RUN uv sync --locked

COPY Docker/rag/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]