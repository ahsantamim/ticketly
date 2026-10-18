"""Test settings. Self-contained so the test suite never depends on a local .env file."""

from django.core.management.utils import get_random_secret_key

from .base import *  # noqa: F403
from .base import BASE_DIR, env

SECRET_KEY = get_random_secret_key()
DEBUG = False
ALLOWED_HOSTS = ["testserver"]

# DATABASE_URL comes from the real environment only (never .env), so the Docker test
# service runs against Postgres while a bare `uv run pytest` stays on SQLite.
# pytest-django creates and drops a separate test_<NAME> database either way.
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
