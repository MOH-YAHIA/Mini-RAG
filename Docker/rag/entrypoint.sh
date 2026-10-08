#!/bin/sh

set -e

uv run alembic -c ./database/alembic.ini upgrade head

exec uv run uvicorn main:app --host 0.0.0.0 --port 8000