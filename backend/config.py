import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default-secret-key")
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    USE_CORS = True
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Custom
    ADMIN = os.environ.get("ADMIN", "arctic.fox.flask@outlook.com")
    POSTS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 30
    FOLLOWERS_PER_PAGE = 50
    # Flask-Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.office365.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SUBJECT_PREFIX = '[Arctic Fox]'
    MAIL_SENDER = f'Arctic Fox Admin <{ADMIN}>'
    MAIL_FOR_TEST_OR_DEBUG = os.environ.get("MAIL_FOR_TEST_OR_DEBUG")
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
    REFRESH_TOKEN_IN_BODY = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", \
        "sqlite:///" + os.path.join(basedir, "dev-data.sqlite")).replace('postgres', 'postgresql')
    ACCESS_TOKEN_MINUTES = 300
    REFRESH_TOKEN_DAYS = 300


class TestingConfig(Config):
    FLASK_RUN_PORT = 5001
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", \
        "sqlite:///" + os.path.join(basedir, "test-data.sqlite"))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", \
        "sqlite:///" + os.path.join(basedir, "data.sqlite"))
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    

config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}