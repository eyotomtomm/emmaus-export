"""Settings for Vercel deployment."""

from .base import *  # noqa: F403
from .base import BASE_DIR
from .base import MIDDLEWARE
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="emmaus-vercel-secret-change-in-production",
)
ALLOWED_HOSTS = ["*"]

# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/db.sqlite3",
    }
}

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

# STATIC FILES
# ------------------------------------------------------------------------------
# WhiteNoise serves from finders (emmaus/static/) without collectstatic
STATIC_ROOT = str(BASE_DIR / "staticfiles")
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
