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
        "HOST": "localhost",
        "PORT": 7654,
    }
}
# No password validation
AUTH_PASSWORD_VALIDATORS = []
# Static Files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# MongoDB
MONGO_DB = "educalegal"
MONGO_ALIAS = "default"
MONGO_USERNAME = "educalegal"
MONGO_PASSWORD = "educalegal"
MONGO_HOST = "localhost"
MONGO_PORT = 27017

CELERY_BROKER_URL = "amqp://educalegal:educalegal@localhost/educalegal"