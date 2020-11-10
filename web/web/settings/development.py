from .base import *
from django.contrib.messages import constants as message_constants

ALLOWED_HOSTS = ["*"]
# Debug messages
DEBUG = True
MESSAGE_LEVEL = message_constants.DEBUG
# Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# The middleware placement is sensitive. If the middleware before silk.middleware.SilkyMiddleware returns from process_
# request then SilkyMiddleware will never get the chance to execute. Therefore you must ensure that any middleware
# placed before never returns anything from process_request.
SILK = True
MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
INSTALLED_APPS += ["silk"]
# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "educalegal",
        "USER": "educalegal",
        "PASSWORD": "educalegal",
        "HOST": "db",
        "PORT": 7654,
    }
}
# No password validation
AUTH_PASSWORD_VALIDATORS = []

# Static e media files
# https://www.digitalocean.com/community/questions/getting-signaturedoesnotmatch-with-digitalocean-spaces
AWS_STORAGE_BUCKET_NAME = "educalegal-test"
AWS_S3_ENDPOINT_URL = "https://educalegal-test.sfo2.digitaloceanspaces.com/"
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
