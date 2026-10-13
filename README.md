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
uv run python manage.py runserver
curl localhost:8000/api/health/   # {"status":"ok"}
```

Don't run `migrate` yet. The custom user model lands in TIC-7, and it must exist before the first migration.

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
| `config.settings.test` | `pytest` (forced via `--ds`) | Self-contained; no `.env` needed. |
| `config.settings.prod` | `wsgi.py` / `asgi.py` (default) | Requires `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`. |

## Layout

- `config/`: project settings, URLs, and the health endpoint
- `accounts/`, `venues/`, `events/`: domain apps
- `tests/`: pytest suite
