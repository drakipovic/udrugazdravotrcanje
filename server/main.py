import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth

from server.config import DevelopmentConfig, ProductionConfig, TestConfig


app = Flask('server')


if os.environ.get('PROD', None):
    app.config.from_object(ProdConfig)
else:
    app.config.from_object(TestConfig if os.environ.get('TEST', None) else DevelopmentConfig)


db = SQLAlchemy(app)
api = Api(app, prefix='/api')
auth = HTTPBasicAuth()

handler = RotatingFileHandler('server.log', maxBytes=10000, backupCount=2)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)