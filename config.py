from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn


class Config(BaseSettings):
    ALCHEMICAL_ECHO: bool = False
    POSTGRES_URI: PostgresDsn = 'postgresql://username:password@localhost/db'
    ALCHEMICAL_DATABASE_URL: str = str(POSTGRES_URI)

    SECRET_KEY: str = 'secret'
    DISABLE_AUTH: bool = False
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 30

    CACHE_TYPE: str = 'redis'
    REDIS_URL: RedisDsn

    AWS_REGION: str = 'us-east-1'
    AWS_BUCKET: str = 'arctic-fox'
    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''

    GOOGLE_CLIENT_ID: str = ''
    GOOGLE_CLIENT_SECRET: str = ''
    GOOGLE_REDIRECT_URI: str = ''

    APIFAIRY_TITLE: str = 'Arctic Fox API'
    APIFAIRY_VERSION: str = '1.0'
    APIFAIRY_UI: str = 'swagger_ui'
    APIFAIRY_UI_PATH: str = '/api'

    MAIL_SERVER: str = 'localhost'
    MAIL_PORT: int = 25
    MAIL_USE_TLS: bool = False
    MAIL_USERNAME: str = ''
    MAIL_PASSWORD: str = ''
    MAIL_DEFAULT_SENDER: str = ''
    ADMIN_EMAIL: str = ''
    ERROR_EMAIL: str = ''

    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

    class Config:
        env_file = '.env'
        env_prefix = 'AF_'
        extra = 'ignore'
        case_sensitive = False


config: Config = Config()
