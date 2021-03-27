from .base import *

from django.contrib.messages import constants as message_constants

ALLOWED_HOSTS = ["app.educalegal.com.br", "api.educalegal.com.br", "134.122.5.207"]

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
        "HOST": "educa-legal-producao-db-postgresql-do-user-8910843-0.b.db.ondigitalocean.com",
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
# Static e media files
# https://www.digitalocean.com/community/questions/getting-signaturedoesnotmatch-with-digitalocean-spaces
AWS_STORAGE_BUCKET_NAME = "educalegal-app"
AWS_S3_ENDPOINT_URL = "https://educa-legal-files-app.nyc3.digitaloceanspaces.com/"
AWS_STATIC_LOCATION = "static"
STATIC_URL = "{}/{}/".format(AWS_S3_ENDPOINT_URL, AWS_STATIC_LOCATION)
AWS_MEDIA_LOCATION = "media"
MEDIA_URL = "{}/{}/".format(AWS_S3_ENDPOINT_URL, AWS_MEDIA_LOCATION)

# MongoDB
MONGO_DB = "educalegal"
MONGO_ALIAS = "default"
MONGO_USERNAME = "educalegal"
MONGO_PASSWORD = "educalegal"
MONGO_HOST = "apimongo"
MONGO_PORT = 27017
