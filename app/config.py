import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SEKRET_KEY', 'ah12')
    DEBUG = False


class DevConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    #     os.path.join(basedir, 'dev_trankat.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'pro_trankat.db')
    # os.path.join(basedir, 'main_watering_sys_db.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(dev=DevConfig, pro=ProductionConfig)
key = Config.SECRET_KEY
