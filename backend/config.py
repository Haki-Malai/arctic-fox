import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default-secret-key")
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Custom
    ADMIN = os.environ.get("ADMIN", "admin@arctic-fox.com")
    POSTS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 30
    FOLLOWERS_PER_PAGE = 50
    # Flask-Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in \
        ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SUBJECT_PREFIX = '[Arctic Fox]'
    MAIL_SENDER = f'Arctic Fox Admin <{ADMIN}>'
    SLOW_DB_QUERY_TIME = 0.5
    # APIFairy
    APIFAIRY_TITLE = os.environ.get("APIFAIRY_TITLE", "Arctic Fox")
    APIFAIRY_VERSION = os.environ.get("APIFAIRY_VERSION", "v1")
    APIFAIRY_DESCRIPTION = os.environ.get("APIFAIRY_DESCRIPTION", "Arctic Fox is a simple blog app written in Python and Flask.")
    APIFAIRY_DOCS = os.environ.get("APIFAIRY_DOCS", "Arctic Fox Documentation")
    # Tokens
    REFRESH_TOKEN_IN_COOKIE = False
    ACCESS_TOKEN_MINUTES = 30
    REFRESH_TOKEN_DAYS = 30
    REFRESH_TOKEN_IN_BODY = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", \
        "sqlite:///" + os.path.join(basedir, "dev-data.sqlite"))
    SESSION_COOKIE_SECURE = False
    SESSION_PERMAMENT = True
    ACCESS_TOKEN_MINUTES = 30000
    REFRESH_TOKEN_DAYS = 30000
    

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", \
        "sqlite:///" + os.path.join(basedir, "test-data.sqlite"))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", \
        "sqlite:///" + os.path.join(basedir, "data.sqlite"))
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    SESSION_PERMAMENT = False
    

config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}