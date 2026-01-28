from .base import *

DEBUG = True

ALLOWED_HOSTS = []

# Use SQLite for local dev (simpler, no Docker required)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
