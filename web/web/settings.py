"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "mvyzst83ep^g72ho)29dm+zq&+we8qbg82u8q_(_7$$a=i_@*n"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SILK = False

if "ALLOWED_HOSTS" in os.environ:
    allowed_hosts_string = os.environ["ALLOWED_HOSTS"]
    hosts = allowed_hosts_string.split(",")
    ALLOWED_HOSTS = hosts
else:
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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
    # Not sure yet what it does...
    "corsheaders",
    # Alternative storage for files in Django
    "storages",
    # Driver for AWS Compatible storage
    "boto3",
    # Integration with Boostrap 4
    "bootstrap4",
    # Local
    "tenant",
    "users",
    "school",
    "interview",
    "api",
    "document",
]

if not DEBUG:
    INSTALLED_APPS.append("google_analytics")

if SILK:
    INSTALLED_APPS.append("silk")

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")


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


# The middleware placement is sensitive. If the middleware before silk.middleware.SilkyMiddleware returns from process_
# request then SilkyMiddleware will never get the chance to execute. Therefore you must ensure that any middleware
# placed before never returns anything from process_request.
if SILK:
    MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")

if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

# The Debug Toolbar is shown only if your IP address is listed in the INTERNAL_IPS setting. This means that for local
# development, you must add '127.0.0.1' to INTERNAL_IPS; you’ll need to create this setting if it doesn’t already exist
# in your settings module:

INTERNAL_IPS = ["127.0.0.1"]


ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if "DATABASE_NAME" in os.environ:
    # Use this with docker-compose
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DATABASE_NAME"],
            "USER": os.environ["DATABASE_USER"],
            "PASSWORD": os.environ["DATABASE_PASSWORD"],
            "HOST": os.environ["DATABASE_HOST"],
            "PORT": os.environ["DATABASE_PORT"],
        }
    }
else:
    # Use this with postresql on localhost
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "educalegal",
            "USER": "educalegal",
            "PASSWORD": "educalegal",
            "HOST": "localhost",
            "PORT": 7654,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-scalable-django-app-with-digitalocean-managed-databases-and-spaces

if "USE_DIGITAL_OCEAN_SPACES" in os.environ:
    # https://www.digitalocean.com/docs/spaces/how-to/manage-access/
    AWS_ACCESS_KEY_ID = "AWNYACZSFSYOBCIOTFOP"
    AWS_SECRET_ACCESS_KEY = "k0GW8r3VnC9GzKD7S6RTdjCP2dVzN3bfOdthVfSCY/g"
    # https://www.digitalocean.com/community/questions/getting-signaturedoesnotmatch-with-digitalocean-spaces
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_STORAGE_BUCKET_NAME = "educalegal-app"
    AWS_S3_ENDPOINT_URL = "https://educalegal-app.nyc3.digitaloceanspaces.com/"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_LOCATION = "static"
    AWS_DEFAULT_ACL = "public-read"

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    STATIC_URL = "{}/{}/".format(AWS_S3_ENDPOINT_URL, AWS_LOCATION)
    STATIC_ROOT = "static/"

else:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")

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
ACCOUNT_FORMS = {"signup": "tenant.forms.EducaLegalSignupForm"}


# E-mail sending Settings
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = "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"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "sistemas@educalegal.com.br"



# API Settings
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Session Authentication is kept here for the browseable API
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    # https://www.django-rest-framework.org/api-guide/throttling/
    # "DEFAULT_THROTTLE_CLASSES": [
    #     "rest_framework.throttling.AnonRateThrottle",
    #     "rest_framework.throttling.UserRateThrottle",
    # ],
    # "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "10000/day"},
}


CORS_ORIGIN_WHITELIST = (
    "http://localhost:3000",
    "http://localhost:8000",
    "https://docs.educalegal.com.br",
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
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join(BASE_DIR, "media/info.log"),
        },
    },
    "loggers": {"": {"level": "DEBUG", "handlers": ["console", "file"]}},
}

# Google Analytics django-google-analytics-app
GOOGLE_ANALYTICS = {
    'google_analytics_id': 'UA-149363385-1',
}