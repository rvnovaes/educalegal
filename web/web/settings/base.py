import os
import moneyed
from moneyed.localization import _FORMATTER
from decimal import ROUND_HALF_EVEN
from datetime import timedelta


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "mvyzst83ep^g72ho)29dm+zq&+we8qbg82u8q_(_7$$a=i_@*n"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.postgres',
    # 3rd party ==========================================
    # Nice Boostrap Forms
    "crispy_forms",
    # App authentication, passoword recovery, social auth facilities
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Easy and simple tables for Django and filtering for tables
    "django_tables2",
    "django_filters",
    # Good Old Rest Framework
    "rest_framework",
    # Generates the tokens on the server for Rest Framework
    "rest_framework.authtoken",
    # Endpoints for authentication on Rest Framework
    "rest_auth",
    # Swagger -> https://github.com/axnsan12/drf-yasg
    "drf_yasg",
    # Not sure yet what it does...
    "corsheaders",
    # Alternative storage for files in Django
    "storages",
    # Driver for AWS Compatible storage
    "boto3",
    # Integration with Boostrap 4
    "bootstrap4",
    # Django models currency
    "djmoney",
    # Resultados do celery no banco do Django
    "django_celery_results",
    # https://github.com/izimobil/django-rest-framework-datatables
    "rest_framework_datatables",
    # Local
    "tenant",
    "users",
    "school",
    "interview",
    "api",
    "document",
    "billing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

FILE_UPLOAD_TEMP_DIR = "/upload_temp_dir"


# The Debug Toolbar is shown only if your IP address is listed in the INTERNAL_IPS setting. This means that for local
# development, you must add '127.0.0.1' to INTERNAL_IPS; you’ll need to create this setting if it doesn’t already exist
# in your settings module:
INTERNAL_IPS = ["127.0.0.1"]
ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"),],
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

WSGI_APPLICATION = "web.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = "users.CustomUser"

CRISPY_TEMPLATE_PACK = "bootstrap4"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# AllAuth --> https://wsvincent.com/django-login-with-email-not-username/

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = None
# The issue is that django-allauth ’s ACCOUNT_LOGOUT_REDIRECT actually overrides the
# built-in LOGOUT_REDIRECT_URL , however, since they both point to the homepage this
# change may not be apparent. To future-proof our application since maybe we don’t
# want to always redirect to the homepage on logout, we should be explicit here with
# the logout redirect.
LOGIN_REDIRECT_URL = "interview:interview-list"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_FORMS = {"signup": "tenant.forms.EducaLegalSignupForm",
                 'change_password': 'users.forms.CustomUserChangePasswordForm'}
ACCOUNT_ADAPTER = 'users.adaptor.CustomUserAccountAdapter'

# E-mail sending Settings
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = (
    "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"
)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "sistemas@educalegal.com.br"


# API Settings
LOGIN_URL = "/api/v2/login"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
}


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Session Authentication is kept here for the browseable API
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,

    # https://www.django-rest-framework.org/api-guide/throttling/
    # "DEFAULT_THROTTLE_CLASSES": [
    #     "rest_framework.throttling.AnonRateThrottle",
    #     "rest_framework.throttling.UserRateThrottle",
    # ],
    # "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "10000/day"},
    # 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema' => Usado para CoreAPI (Deprecado)
}


CORS_ORIGIN_WHITELIST = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {"format": "%(name)-12s %(levelname)-8s %(message)s"},
        "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
        "django_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join(BASE_DIR, "media/debug.log"),
        },
        "info_log": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join(BASE_DIR, "media/info.log"),
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console", "info_log"]},
        "django": {
            "level": "INFO",
            "handlers": ["console", "django_file"],
            "propagate": False,
        },
        # O Log de autoreload pode ser super verboso.
        "django.utils.autoreload": {
            "level": "INFO",
            "handlers": ["django_file"],
            "propagate": False,
        },
    },
}

# Adding a new Currency
BRL = moneyed.add_currency(
    code="BRL", numeric="986", name="Brazilian Real", countries=("BRAZIL",)
)

# Currency Formatter will output R$ 2.000,00
_FORMATTER.add_sign_definition("default", BRL, prefix=u"R$ ")

_FORMATTER.add_formatting_definition(
    "pt_BR",
    group_size=3,
    group_separator=".",
    decimal_point=",",
    positive_sign="",
    trailing_positive_sign="",
    negative_sign="-",
    trailing_negative_sign="",
    rounding_method=ROUND_HALF_EVEN,
)

CURRENCIES = ("BRL",)

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'amqp://educalegal:educalegal@educalegal_rabbitmq/educalegal'