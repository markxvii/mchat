import os
import sys

basedir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN=sys.platform.startswith('win')
if WIN:
    prefix='sqlite:///'
else:
    prefix='sqlite:////'


class BaseConfig:
    SECRET_KEY=os.getenv('SECRET_KEY','key')

    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL',prefix+os.path.join(basedir,'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    MESSAGE_PER_PAGE=30

class DevelopmentConfig(BaseConfig):
    pass

class ProductionConfig(BaseConfig):
    pass

class TestingConfig(BaseConfig):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    WTF_CSRF_ENABLED=False


config={
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing':TestingConfig
}