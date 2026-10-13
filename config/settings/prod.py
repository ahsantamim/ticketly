"""Production settings. Every value must come from the real environment; there are no defaults."""

from .base import *  # noqa: F403
from .base import env

SECRET_KEY = env("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

DATABASES = {
    "default": env.db("DATABASE_URL"),
}
