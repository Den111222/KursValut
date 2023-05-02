import logging
from logging.config import dictConfig

from flask import Flask
from flask.logging import default_handler

from config import LOGGING

dictConfig(LOGGING)
app = Flask(__name__)

app.logger = logging.getLogger('GoldenEye')
app.logger.removeHandler(default_handler)

import views