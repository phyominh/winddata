import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {'db': os.environ.get('DEV_MONGODB_NAME')}

class ProductionConfig(Config):
    DEBUG = False
    MONGODB_SETTINGS = {'db': os.environ.get('PROD_MONGODB_NAME')}

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
