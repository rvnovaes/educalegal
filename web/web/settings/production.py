from .base import *

from django.contrib.messages import constants as message_constants

ALLOWED_HOSTS = ["app.educalegal.com.br", "167.71.161.48"]

DEBUG = False
MESSAGE_LEVEL = message_constants.INFO
SILK = False
# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "educa-legal-app",
        "USER": "educa-legal-app",
        "PASSWORD": "e60k17byidfg20ye",
        "HOST": "educa-legal-producao-db-postgresql-do-user-106912-0.db.ondigitalocean.com",
        "PORT": 25060
    }
}
# Validate passwords
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]
# Static Files
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
# MongoDB
MONGO_DB = "educalegal"
MONGO_ALIAS = "default"
MONGO_USERNAME = "educalegal"
MONGO_PASSWORD = "educalegal"
MONGO_HOST = "mongo"
MONGO_PORT = 27017