import json
import os
from datetime import timedelta
from os.path import join

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from settings import const as settings_const

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Local development settings
LOCAL_DEVELOPMENT_AUTHENTICATION = (
    os.getenv("LOCAL_DEVELOPMENT_AUTHENTICATION", False) == "True"
)

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # Third party apps
    "rest_framework",  # utilities for rest apis
    "django_filters",  # for filtering rest endpoints,
    "drf_spectacular",  # for generating real OpenAPI 3.0 documentation
    "constance",
    "constance.backends.database",  # for dynamic configurations in admin
    "mozilla_django_oidc",  # for authentication
    # Your apps
    "apps.users",
    "apps.itinerary",
    "apps.cases",
    "apps.accesslogs",
    "apps.planner",
    "apps.fraudprediction",
    "apps.visits",
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
    "apps.accesslogs.middleware.LoggingMiddleware",
)

ROOT_URLCONF = "settings.urls"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
WSGI_APPLICATION = "app.wsgi.application"

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ADMINS = (("Author", "p.curet@mail.amsterdam.nl"),)

# Database
DEFAULT_DATABASE_NAME = "default"
BWV_DATABASE_NAME = "bwv"

DATABASES = {
    DEFAULT_DATABASE_NAME: {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST", "database"),
        "PORT": "5432",
    },
    BWV_DATABASE_NAME: {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("BWV_DB_NAME"),
        "USER": os.environ.get("BWV_DB_USER"),
        "PASSWORD": os.environ.get("BWV_DB_PASSWORD"),
        "HOST": os.environ.get("BWV_DB_HOST", "bwv_db"),
        "PORT": "5432",
    },
}

# General
APPEND_SLASH = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_L10N = True
USE_TZ = True

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
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# Mail
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS and allowed hosts
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(",")
CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ORIGIN_WHITELIST").split(",")
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
CONSTANCE_PLANNER_SETTINGS_KEY = "PLANNER_SETTINGS"

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
    CONSTANCE_PLANNER_SETTINGS_KEY: (
        json.dumps(settings_const.EXAMPLE_PLANNER_SETTINGS),
        "Settings for planning and generating lists",
    ),
}

# Error logging through Sentry
sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"), integrations=[DjangoIntegration()])

OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET")
OIDC_USERNAME_ALGO = "apps.users.utils.generate_username"

ACCEPTANCE_OIDC_REDIRECT_URL = "https://acc.top.amsterdam.nl/authentication/callback"
PRODUCTION_OIDC_REDIRECT_URL = "https://top.amsterdam.nl/authentication/callback"

OIDC_REDIRECT_URL = ACCEPTANCE_OIDC_REDIRECT_URL

if ENVIRONMENT == "production":
    OIDC_REDIRECT_URL = PRODUCTION_OIDC_REDIRECT_URL

OIDC_RP_SIGN_ALGO = "RS256"

OIDC_RP_SCOPES = "openid"

OIDC_VERIFY_SSL = True

# https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/.well-known/openid-configuration
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv(
    "OIDC_OP_AUTHORIZATION_ENDPOINT",
    "https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/authorize",
)
OIDC_OP_TOKEN_ENDPOINT = os.getenv(
    "OIDC_OP_TOKEN_ENDPOINT", "https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/token"
)
OIDC_OP_USER_ENDPOINT = os.getenv(
    "OIDC_OP_USER_ENDPOINT", "https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/userinfo"
)
OIDC_OP_JWKS_ENDPOINT = os.getenv(
    "OIDC_OP_JWKS_ENDPOINT",
    "https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/.well-known/jwks.json",
)

OIDC_USE_NONCE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": "DEBUG"},
    },
    "loggers": {
        "woonfraude_model": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "mozilla_django_oidc": {"handlers": ["console"], "level": "DEBUG"},
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=4),
    # We don't refresh tokens yet, so we set refresh lifetime to zero
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=0),
}

ACCESS_LOG_EXEMPTIONS = ("/looplijsten/health",)

# BRK Access request settings
BRK_ACCESS_CLIENT_ID = os.getenv("BRK_ACCESS_CLIENT_ID")
BRK_ACCESS_CLIENT_SECRET = os.getenv("BRK_ACCESS_CLIENT_SECRET")
BRK_ACCESS_URL = os.getenv("BRK_ACCESS_URL")
BRK_API_OBJECT_EXPAND_URL = os.getenv(
    "BRK_API_OBJECT_EXPAND_URL", "https://acc.api.data.amsterdam.nl/brk/object-expand/"
)

# BAG Access request settings
BAG_API_SEARCH_URL = "https://api.data.amsterdam.nl/atlas/search/adres/"

# Zaken Access request settings
# TODO: Fix this later with proper environment variables
if ENVIRONMENT == "acceptance":
    ZAKEN_API_URL = os.getenv(
        "ZAKEN_API_URL", "https://acc.looplijst.top.amsterdam.nl/api/v1"
    )
else:
    ZAKEN_API_URL = os.getenv("ZAKEN_API_URL", None)

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

FRAUD_PREDICTION_CACHE_DIR = os.path.normpath(
    join(os.path.dirname(BASE_DIR), "fraud_prediction_cache")
)
# Secret key for accessing fraud prediction scoring endpoint
FRAUD_PREDICTION_SECRET_KEY = os.environ.get("FRAUD_PREDICTION_SECRET_KEY")

# City central geolocation and postal code range
CITY_CENTRAL_LOCATION_LAT = 52.379189
CITY_CENTRAL_LOCATION_LNG = 4.899431
CITY_MIN_POSTAL_CODE = 1000
CITY_MAX_POSTAL_CODE = 1109

# Secret key for accessing ZAKEN
SECRET_KEY_TOP_ZAKEN = os.environ.get("SECRET_KEY_TOP_ZAKEN", None)
# Connect to Decos Join
DECOS_JOIN_API = "https://decosdvl.acc.amsterdam.nl:443/decosweb/aspx/api/v1/items/"
DECOS_JOIN_USERNAME = os.getenv("DECOS_JOIN_USERNAME", None)
DECOS_JOIN_PASSWORD = os.getenv("DECOS_JOIN_PASSWORD", None)
DECOS_JOIN_BANDB_ID = "D8D961993D7E478D9B644587822817B1"
DECOS_JOIN_VAKANTIEVERHUUR_ID = "TBD"
DECOS_JOIN_BOOK_KNOWN_BAG_OBJECTS = "90642DCCC2DB46469657C3D0DF0B1ED7"
DECOS_JOIN_BOOK_UNKNOWN_BOOK = "B1FF791EA9FA44698D5ABBB1963B94EC"
USE_DECOS_MOCK_DATA = True


# SUBJECTS FOR ZAKEN SYSTEEM TIMELINE
TIMELINE_SUBJECT_VISIT = "Bezoek"
