# syntax=docker/dockerfile:1

# Debian slim (glibc): prebuilt wheels like psycopg-binary install as-is, unlike musl-based Alpine.
# Trixie (current Debian stable) is ~16 MB smaller than bookworm.
ARG PYTHON_IMAGE=python:3.12-slim-trixie

# --- builder: resolve dependencies into /app/.venv with uv ---
FROM ${PYTHON_IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /usr/local/bin/uv

# Use the image's Python (never download one) so the venv works in the runtime stage.
# No precompiled .pyc: it adds ~14 MB, and the image has a <250 MB budget.
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Only the lockfile and pyproject feed this layer, so code edits don't reinstall dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# --- dev: adds the dev group (pytest, ruff) for running tests in a container. Never shipped. ---
FROM builder AS dev

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY . .

CMD ["pytest"]

# --- runtime (default target): slim image with only the venv and the code, run as non-root ---
FROM ${PYTHON_IMAGE} AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /app

# Files stay root-owned, so the app user can read the code but not modify it.
COPY --from=builder /app/.venv /app/.venv
COPY . .

USER app

EXPOSE 8000

# config.wsgi defaults to config.settings.prod.
# --no-control-socket: Gunicorn's gunicornc socket defaults to $HOME/.gunicorn, and the app user
# has no home directory. Containers are managed through Docker, not gunicornc.
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--no-control-socket"]
