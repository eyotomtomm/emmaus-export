"""Settings for cPanel shared hosting (Passenger).

Why this exists rather than reusing production.py: production.py expects Redis
for CACHES and S3 for storage, neither of which a shared cPanel package has.
This module keeps the security posture but swaps in local-memory caching,
SQLite on the account's own disk, and WhiteNoise for static files.
"""

from .base import *  # noqa: F403
from .base import BASE_DIR
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = False
# No default on purpose: an unset key should fail loudly at boot, not silently
# ship a known secret. Set it in the Python App's environment variables.
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["emmausimportexport.com", "www.emmausimportexport.com"],
)

# DATABASES
# ------------------------------------------------------------------------------
# SQLite is fine here: the site is read-only brochure content, and unlike
# Vercel's ephemeral /tmp, the cPanel home directory persists between restarts.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
        "ATOMIC_REQUESTS": True,
    },
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
# WhiteNoise middleware is already in base.MIDDLEWARE. Run collectstatic and it
# serves hashed, compressed assets straight from the app - no Apache alias or
# public_html symlink needed.
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# SECURITY
# ------------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Deliberately defaults to False. The domain currently has only a self-signed
# certificate; forcing the HTTPS redirect before AutoSSL has issued a real one
# would push every visitor into a browser security warning. Flip this to True
# (and raise HSTS) once the certificate shows as valid in cPanel.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=False,
)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[
        "https://emmausimportexport.com",
        "https://www.emmausimportexport.com",
    ],
)

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("DJANGO_EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("DJANGO_EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="info@emmausimportexport.com",
)
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

# LOGGING
# ------------------------------------------------------------------------------
# Passenger discards stdout, so log to a file inside the app instead.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "django.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["file"]},
}
