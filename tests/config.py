from config import Config


class TestConfig(Config):
    SERVER_NAME: str = 'localhost:5000'
    TESTING: bool = True
    DISABLE_AUTH: bool = True
    ALCHEMICAL_DATABASE_URL: str = 'sqlite:///:memory:' # in-memory database


test_config: TestConfig = TestConfig()
