import os
import sys
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: str = "False") -> bool:
    value = os.environ.get(name, default)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def env_allowed_hosts(name: str, default: str) -> list[str]:
    raw = os.environ.get(name, default)
    hosts: list[str] = []
    for item in raw.split(","):
        candidate = item.strip()
        if not candidate:
            continue
        # Permite pegar URL completa de Render y normaliza a host.
        if "://" in candidate:
            parsed = urlparse(candidate)
            candidate = parsed.hostname or ""
        else:
            # Limpia rutas accidentales: ejemplo "app.onrender.com/".
            candidate = candidate.split("/")[0]
        candidate = candidate.strip()
        if candidate:
            hosts.append(candidate)
    return hosts


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "change-this-in-prod-please-use-a-strong-secret-key",
)

DEBUG = env_bool("DJANGO_DEBUG", "False")

default_hosts = "localhost,127.0.0.1" if DEBUG else ""
ALLOWED_HOSTS = env_allowed_hosts("DJANGO_ALLOWED_HOSTS", default_hosts)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.users",
]

# Django model references use app_label.ModelName
AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "usuarios_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "usuarios_service.wsgi.application"

# Base de datos:
# - Produccion: DATABASE_URL (ej. PostgreSQL en Neon)
# - Desarrollo local: SQLite por defecto
DATABASE_URL = os.environ.get("DATABASE_URL")
RUNNING_TESTS = "test" in sys.argv
USE_SQLITE_FOR_TESTS = env_bool("USE_SQLITE_FOR_TESTS", "True")

if DATABASE_URL and not (RUNNING_TESTS and USE_SQLITE_FOR_TESTS):
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "600")),
            ssl_require=env_bool("DB_SSL_REQUIRE", "True"),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Cache:
# - Produccion: Redis si REDIS_URL esta definido.
# - Desarrollo/CI local: memoria en proceso como fallback.
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "usuarios-local-cache",
        }
    }

# Base de seguridad de API:
# - JWT para llamadas entre servicios/clientes
# - SessionAuthentication para admin web de Django
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("THROTTLE_ANON_RATE", "60/min"),
        "user": os.environ.get("THROTTLE_USER_RATE", "120/min"),
        "register": os.environ.get("THROTTLE_REGISTER_RATE", "5/min"),
    },
}

SIMPLE_JWT = {
    # Si no se define, usa SECRET_KEY. Permite desacoplar firma JWT del secreto de Django.
    "SIGNING_KEY": os.environ.get("JWT_SIGNING_KEY", SECRET_KEY),
    "ALGORITHM": os.environ.get("JWT_ALGORITHM", "HS256"),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "30"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Endurecimiento basico para despliegue detras de proxy HTTPS (PaaS).
PRODUCTION_HARDENING_DEFAULT = not DEBUG and not RUNNING_TESTS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT", "True" if PRODUCTION_HARDENING_DEFAULT else "False"
)
SESSION_COOKIE_SECURE = env_bool(
    "DJANGO_SESSION_COOKIE_SECURE", "True" if PRODUCTION_HARDENING_DEFAULT else "False"
)
CSRF_COOKIE_SECURE = env_bool(
    "DJANGO_CSRF_COOKIE_SECURE", "True" if PRODUCTION_HARDENING_DEFAULT else "False"
)
SECURE_HSTS_SECONDS = int(
    os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000" if PRODUCTION_HARDENING_DEFAULT else "0")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "True" if PRODUCTION_HARDENING_DEFAULT else "False"
)
SECURE_HSTS_PRELOAD = env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD", "True" if PRODUCTION_HARDENING_DEFAULT else "False"
)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
