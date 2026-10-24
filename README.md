# ticketly

Event ticketing API built with Django and Django REST Framework.

## Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs Python 3.12 for you if needed.

```sh
git clone git@github.com:ahsantamim/ticketly.git
cd ticketly
uv sync
cp .env.example .env
uv run pre-commit install
```

Dependencies are managed with uv and pinned in `uv.lock`.

## Run

```sh
uv run python manage.py migrate
uv run python manage.py runserver
curl localhost:8000/api/health/   # {"status":"ok"}
```

## Docker

Runs the API under Gunicorn against Postgres 16. Needs Docker with Compose v2; no `.env` required.

```sh
make up        # docker compose up --build -d
curl localhost:8000/api/health/   # {"status":"ok"}
make migrate   # apply migrations to the Docker Postgres
make test      # pytest inside a container, against Postgres
make shell     # Django shell in the web container
make logs      # follow web logs
make down      # stop; DB data stays in the pgdata volume
```

`make migrate` runs the last built `web` image, so run `make up` first after changing models. `docker compose down -v` deletes the database volume.

The image is built from `python:3.12-slim-trixie` in two stages (uv resolves dependencies in a builder, and the runtime stage copies only the venv and the code). It runs as the non-root `app` user. The `dev` target adds pytest and is used only by `make test`.

## Test and lint

```sh
uv run pytest
uv run pre-commit run --all-files
```

## Settings

Settings live in `config/settings/` and are chosen by `DJANGO_SETTINGS_MODULE`. Config comes from environment variables; see `.env.example`.

| Module | Used by | Notes |
|---|---|---|
| `config.settings.dev` | `manage.py` (default) | Reads `.env`. `DEBUG=True`, SQLite by default. |
| `config.settings.test` | `pytest` (forced via `--ds`) | Ignores `.env`. SQLite unless `DATABASE_URL` is set in the environment (Docker sets it). |
| `config.settings.prod` | `wsgi.py` / `asgi.py` (default) | Requires `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`. |

## Layout

- `config/`: project settings, URLs, and the health endpoint
- `accounts/`, `venues/`, `events/`: domain apps
- `tests/`: pytest suite
- `docs/adr/`: architecture decision records
