import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


def as_bool(value: str) -> bool:
    """Converts a string to a boolean value.

    :param value: The string to convert.

    :returns: The boolean value.
    """
    if value:
        return value.lower() in ['true', 'yes', 'on', '1']
    return False


class Config:
    # Database options
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')

    ALCHEMICAL_DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    ALCHEMICAL_ENGINE_OPTIONS = {'echo': as_bool(os.environ.get('SQL_ECHO'))}

    # Cache options
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST', 'redis')
    CACHE_REDIS_PORT = os.environ.get('CACHE_REDIS_PORT', '6379')
    CACHE_REDIS_DB = os.environ.get('CACHE_REDIS_DB', '0')
    CACHE_REDIS_URL = os.environ.get(
        'CACHE_REDIS_URL', f'redis://{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/{CACHE_REDIS_DB}')

    # AWS
    AWS_REGION = os.environ.get('AWS_REGION')
    AWS_BUCKET = os.environ.get('AWS_BUCKET')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

    # Security options
    SECRET_KEY = os.environ.get('SECRET_KEY', 'top-secret!')
    DISABLE_AUTH = as_bool(os.environ.get('DISABLE_AUTH'))
    ACCESS_TOKEN_MINUTES = int(os.environ.get('ACCESS_TOKEN_MINUTES') or '15')
    REFRESH_TOKEN_DAYS = int(os.environ.get('REFRESH_TOKEN_DAYS') or '7')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')

    # API documentation
    APIFAIRY_TITLE = 'Arctic Fox API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = os.environ.get('DOCS_UI', 'swagger_ui')
    APIFAIRY_UI_PATH = '/api/docs'

    # Email options
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '25')
    MAIL_USE_TLS = as_bool(os.environ.get('MAIL_USE_TLS'))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMIN_EMAILS = os.environ.get('ADMIN_EMAILS', '').split(',')
    ERROR_EMAIL = os.environ.get('ERROR_EMAIL')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = os.environ.get('REDIS_PORT')
    REDIS_DB = os.environ.get('REDIS_DB')

    # Celery options
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
