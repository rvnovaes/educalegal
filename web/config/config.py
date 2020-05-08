# -*- encoding: utf-8 -*-
import configparser
import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.environ.get('ENV')
logger = logging.getLogger(__name__)

if "EL_ENV" in os.environ:
    EL_ENV = os.environ["EL_ENV"]
else:
    logger.warning('Environment variable EL_ENV is missing. Using localhost environment.')
    EL_ENV = 'localhost'
