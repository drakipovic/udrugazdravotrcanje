import os

class Config(object):
    SECRET_KEY = 'tajna'
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://drakipovic:{}@{}/{}'.format(os.environ.get('UZT_PASSWORD'), 
                                                                        os.environ.get('UZT_DOMAIN'),
                                                                        os.environ.get('UZT_DB_NAME'))


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../dev.db'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'