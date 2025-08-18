import os
import socket
import sys
from datetime import timedelta
from os.path import join

from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace import config_integration

from .azure_settings import Azure

azure = Azure()

config_integration.trace_integrations(["requests", "logging", "postgresql"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Local development settings
LOCAL_DEVELOPMENT_AUTHENTICATION = (
    os.getenv("LOCAL_DEVELOPMENT_AUTHENTICATION", False) == "True"
)
LOCAL_DEVELOPMENT_USE_MULTIPROCESSING = (
    os.getenv("LOCAL_DEVELOPMENT_USE_MULTIPROCESSING", False) == "True"
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # Third party apps
    # "keycloak_oidc",
    "rest_framework",  # utilities for rest apis
    "django_filters",  # for filtering rest endpoints,
    "drf_spectacular",  # for generating real OpenAPI 3.0 documentation
    "constance",
    "django_celery_beat",
    "django_celery_results",
    # Health checks. (Expand when more services become available)
    "health_check",
    "health_check.db",
    "health_check.contrib.migrations",
    "health_check.contrib.celery_ping",
    # Your apps
    "apps.users",
    "apps.itinerary",
    "apps.cases",
    "apps.planner",
    "apps.fraudprediction",
    "apps.visits",
    "apps.health",
    "apps.addresses",
    # Enable admin templates inheritance
    "django.contrib.admin",
)

# https://docs.djangoproject.com/en/2.0/topics/http/middleware/
MIDDLEWARE = (
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "opencensus.ext.django.middleware.OpencensusMiddleware",
)

ROOT_URLCONF = "settings.urls"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
WSGI_APPLICATION = "app.wsgi.application"

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ADMINS = (("Author", "p.curet@mail.amsterdam.nl"),)

# Database
DEFAULT_DATABASE_NAME = "default"

# Django 3.2 fixes warning
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASE_HOST = os.getenv("DATABASE_HOST", "database")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dev")
DATABASE_USER = os.getenv("DATABASE_USER", "dev")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "dev")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_OPTIONS = {"sslmode": "allow", "connect_timeout": 5}

if "azure.com" in DATABASE_HOST:
    DATABASE_PASSWORD = azure.auth.db_password
    DATABASE_OPTIONS["sslmode"] = "require"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "CONN_MAX_AGE": 60 * 5,
        "PORT": DATABASE_PORT,
        "OPTIONS": {"sslmode": "allow", "connect_timeout": 5},
    },
}


# General
APPEND_SLASH = True
LANGUAGE_CODE = "en-us"
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_TZ = True
TIME_ZONE = "Europe/Amsterdam"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "media"))

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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

# Password Validation
# https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
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

# Custom user app
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "apps.users.auth.AuthenticationBackend",
)

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 100,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.users.permissions.IsInAuthorizedRealm",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": ("apps.users.auth.AuthenticationClass",),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
}

# Mail
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS and allowed hosts
ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ORIGIN_WHITELIST").split(",")
CORS_ORIGIN_ALLOW_ALL = False

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]/",
    "TITLE": "Toezicht op pad API",
    "VERSION": "v1",
}

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY = "BRK_AUTHENTICATION_TOKEN"
CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY = "BRK_AUTHENTICATION_TOKEN_EXPIRY"
CONSTANCE_MAPS_KEY = "MAPS_KEY"

CONSTANCE_CONFIG = {
    CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY: (
        "",
        "Authentication token for accessing BRK API",
    ),
    CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY: (
        "",
        "Expiry date for BRK API token",
    ),
    CONSTANCE_MAPS_KEY: ("", "Maps API Key"),
}

TAG_NAME = os.getenv("TAG_NAME", "default-release")

OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET", None)
OIDC_USE_NONCE = False

OIDC_RP_CLIENT_ID = os.environ.get(
    "OIDC_RP_CLIENT_ID", "14c4257b-bcd1-4850-889e-7156c9efe2ec"
)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv(
    "OIDC_OP_AUTHORIZATION_ENDPOINT",
    "https://login.microsoftonline.com/72fca1b1-2c2e-4376-a445-294d80196804/oauth2/v2.0/authorize",
)
OIDC_OP_TOKEN_ENDPOINT = os.getenv(
    "OIDC_OP_TOKEN_ENDPOINT",
    "https://login.microsoftonline.com/72fca1b1-2c2e-4376-a445-294d80196804/oauth2/v2.0/token",
)
OIDC_OP_USER_ENDPOINT = os.getenv(
    "OIDC_OP_USER_ENDPOINT", "https://graph.microsoft.com/oidc/userinfo"
)
OIDC_OP_JWKS_ENDPOINT = os.getenv(
    "OIDC_OP_JWKS_ENDPOINT",
    "https://login.microsoftonline.com/72fca1b1-2c2e-4376-a445-294d80196804/discovery/v2.0/keys",
)

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_OP_ISSUER = os.getenv(
    "OIDC_OP_ISSUER",
    "https://sts.windows.net/72fca1b1-2c2e-4376-a445-294d80196804/",
)

OIDC_TRUSTED_AUDIENCES = f"api://{OIDC_RP_CLIENT_ID}"
OIDC_USE_PKCE = True
OIDC_RP_SCOPES = f"openid email api://{OIDC_RP_CLIENT_ID}/user_impersonation"
LOGIN_URL = "/oidc/authenticate/"

if LOCAL_DEVELOPMENT_AUTHENTICATION:
    OIDC_AUTHENTICATION_CALLBACK_URL = "oidc-authenticate"

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "WARNING")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "root": {"handlers": ["console"], "level": LOGGING_LEVEL},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOGGING_LEVEL,
            "stream": sys.stdout,
        },
        "celery": {
            "level": LOGGING_LEVEL,
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "woonfraude_model": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "apps": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "mozilla_django_oidc": {"handlers": ["console"], "level": LOGGING_LEVEL},
        "celery": {
            "handlers": ["celery", "console"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "": {
            "level": LOGGING_LEVEL,
            "handlers": ["console"],
            "propagate": True,
        },
    },
}

APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

if APPLICATIONINSIGHTS_CONNECTION_STRING:
    # Only log queries when in DEBUG due to high cost
    def filter_traces(envelope):
        if LOGGING_LEVEL == "DEBUG":
            return True
        log_data = envelope.data.baseData
        if "query" in log_data["name"].lower():
            return False
        if log_data["name"] == "GET /":
            return False
        if "applicationinsights" in log_data["message"].lower():
            return False
        return True

    exporter = AzureExporter(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING)
    exporter.add_telemetry_processor(filter_traces)
    OPENCENSUS = {
        "TRACE": {
            "SAMPLER": "opencensus.trace.samplers.ProbabilitySampler(rate=1)",
            "EXPORTER": exporter,
        }
    }
    LOGGING["handlers"]["azure"] = {
        "level": LOGGING_LEVEL,
        "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
        "connection_string": APPLICATIONINSIGHTS_CONNECTION_STRING,
    }
    LOGGING["root"]["handlers"] = ["azure", "console"]
    LOGGING["loggers"]["django"]["handlers"] = ["azure", "console"]
    LOGGING["loggers"][""]["handlers"] = ["azure", "console"]
    LOGGING["loggers"]["apps"]["handlers"] = ["azure", "console"]
    LOGGING["loggers"]["woonfraude_model"]["handlers"] = ["azure", "console"]
    LOGGING["loggers"]["celery"]["handlers"] = ["azure", "console", "celery"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    # We don't refresh tokens yet, so we set refresh lifetime to zero
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=0),
}

ACCESS_LOG_EXEMPTIONS = ("/looplijsten/health",)

BAG_ID_AMSTEL_1 = "0363010012143319"
# BRK Access request settings
BRK_ACCESS_CLIENT_ID = os.getenv("BRK_ACCESS_CLIENT_ID")
BRK_ACCESS_CLIENT_SECRET = os.getenv("BRK_ACCESS_CLIENT_SECRET")
BRK_ACCESS_URL = os.getenv("BRK_ACCESS_URL")
BRK_API_OBJECT_EXPAND_URL = os.getenv(
    "BRK_API_OBJECT_EXPAND_URL", "https://acc.api.data.amsterdam.nl/brk/object-expand/"
)

# BAG Access request settings
BAG_BENKAGG_API_URL = "https://api.data.amsterdam.nl/v1/benkagg/adresseerbareobjecten/"

# Zaken Access request settings
ZAKEN_API_URL = os.getenv("ZAKEN_API_URL", None)
ZAKEN_API_HEALTH_URL = os.getenv("ZAKEN_API_HEALTH_URL", None)
USE_ZAKEN_MOCK_DATA = os.environ.get("USE_ZAKEN_MOCK_DATA", False)

# Allows pushes from Top to Zaken, defaults to True
PUSH_ZAKEN = os.getenv("PUSH_ZAKEN", "True") == "True"

# Settings to improve security
is_secure_environment = True if ENVIRONMENT in ["production", "acceptance"] else False
# NOTE: this is commented out because currently the internal health check is done over HTTP
# SECURE_SSL_REDIRECT = is_secure_environment
SESSION_COOKIE_SECURE = is_secure_environment
CSRF_COOKIE_SECURE = is_secure_environment
DEBUG = not is_secure_environment
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = is_secure_environment
SECURE_HSTS_PRELOAD = is_secure_environment
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Secret key for accessing fraud prediction scoring endpoint
FRAUD_PREDICTION_MODEL_ONDERHUUR = "onderhuur"
FRAUD_PREDICTION_MODELS = [
    FRAUD_PREDICTION_MODEL_ONDERHUUR,
]

# Settings for hitkans api endpoint
ONDERHUUR_HITKANS_API_BASE = os.environ.get(
    "ONDERHUUR_HITKANS_API_BASE", "http://localhost:8000"
)
ONDERHUUR_HITKANS_AUTH_TOKEN = os.environ.get("ONDERHUUR_HITKANS_AUTH_TOKEN")
ONDERHUUR_HITKANS_HEALTH_URL = ONDERHUUR_HITKANS_API_BASE + "/healthcheck"
USE_HITKANS_MOCK_DATA = os.environ.get("USE_HITKANS_MOCK_DATA", "False") == "True"

# City central geolocation and postal code range
CITY_CENTRAL_LOCATION_LAT = 52.379189
CITY_CENTRAL_LOCATION_LNG = 4.899431
CITY_MIN_POSTAL_CODE = 1000
CITY_MAX_POSTAL_CODE = 1384

# Secret key for accessing ZAKEN
SECRET_KEY_TOP_ZAKEN = os.environ.get("SECRET_KEY_TOP_ZAKEN", None)

# AZA for accessing TOP
SECRET_KEY_AZA_TOP = os.getenv("SECRET_KEY_AZA_TOP", None)


def get_redis_url():
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    return f"rediss://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"


REDIS_URL = get_redis_url()
HEALTHCHECK_CELERY_PING_TIMEOUT = 5

CELERY_BROKER_URL = get_redis_url()
BROKER_CONNECTION_MAX_RETRIES = None
BROKER_CONNECTION_TIMEOUT = 120
BROKER_URL = get_redis_url()
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TIMEZONE = "Europe/Amsterdam"
CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "socket_keepalive": True,
    "socket_keepalive_options": {
        socket.TCP_KEEPIDLE: 60,
        socket.TCP_KEEPCNT: 5,
        socket.TCP_KEEPINTVL: 10,
    },
}

SPECTACULAR_DEFAULTS = {
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ]
}

# Default state types defined in AZA by fixtures
AZA_CASE_STATE_TYPES = [
    {
        "id": 235,
        "name": "Huisbezoek",
    },
    {
        "id": 236,
        "name": "Hercontrole",
    },
]
AZA_CASE_STATE_NAMES = (
    "Huisbezoek",
    "Hercontrole",
    "Leegstandsgesprek",
)
AZA_ALLOWED_TASK_NAMES = (
    "task_uitvoeren_leegstandsgesprek",
    "task_create_visit",
)
