import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = 'tajna'
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=100)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://drakipovic:{}@{}:5432/{}'.format(os.environ.get('UZT_PASSWORD'), 
                                                                        os.environ.get('UZT_DOMAIN'),
                                                                        os.environ.get('UZT_DB_NAME'))


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../dev.db'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'