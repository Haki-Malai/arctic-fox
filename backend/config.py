import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    # Session (More info: https://pythonhosted.org/Flask-Session/#configuration)
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default-secret-key")
    SESSION_TYPE = "redis"
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(basedir, "data.sqlite"))
    DEBUG = False
    

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMAMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", "sqlite:///" + os.path.join(basedir, "dev-data.sqlite"))
    

class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMAMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///" + os.path.join(basedir, "test-data.sqlite"))
    

config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}