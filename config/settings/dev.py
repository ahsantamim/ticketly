"""Local development settings. Values come from the environment or a local .env file."""

from .base import *  # noqa: F403
from .base import BASE_DIR, env

env_file = BASE_DIR / ".env"
if env_file.exists():
    env.read_env(env_file)

SECRET_KEY = env("SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}

# Print outgoing mail to the console. Not in base.py, so prod never inherits it
# silently; prod configures a real backend when email ships.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
