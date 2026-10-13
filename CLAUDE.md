# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

Django 6.1 + DRF on Python 3.12, managed with uv (pinned in `uv.lock`). Work is tracked in Linear: project **Ticketly** (team `Ticketlybgb`), issue key `TIC`.

## Commands

- Install: `uv sync`, then `cp .env.example .env`
- Run: `uv run python manage.py runserver` (health: `GET /api/health/`)
- Test: `uv run pytest` (always uses `config.settings.test` via `--ds`)
- Lint and format: `uv run pre-commit run --all-files` (ruff and file hygiene). Only tracked files are checked.

## Architecture

- `config/settings/{base,dev,test,prod}.py`: `manage.py` defaults to dev, and `wsgi`/`asgi` default to prod (fails closed). Config comes from env via django-environ. prod requires `SECRET_KEY`, `ALLOWED_HOSTS` and `DATABASE_URL`.
- DRF requires authentication by default (`IsAuthenticated`). Public views must opt out explicitly.
- Domain apps: `accounts`, `venues`, `events`. Tests live in the top-level `tests/` folder.

## Constraints

- Don't run `migrate` against a database you intend to keep until the custom `User` model (TIC-7) exists.
