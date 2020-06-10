from django.conf import settings

from util.mongo_util import create_mongo_connection

create_mongo_connection(
    settings.MONGO_DB,
    settings.MONGO_ALIAS,
    settings.MONGO_USERNAME,
    settings.MONGO_PASSWORD,
    settings.MONGO_HOST,
    settings.MONGO_PORT,
)