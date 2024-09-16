import unittest

from api.app import create_app, db
from database.models import User
from config import config


class TestConfig(config):
    SERVER_NAME = 'localhost:5000'
    TESTING = True
    DISABLE_AUTH = True
    ALCHEMICAL_DATABASE_URL = 'sqlite://' # in-memory database


class BaseTestCase(unittest.TestCase):
    config = TestConfig

    def setUp(self):
        """Creates a new Flask test client and initializes the database.
        """
        self.app = create_app(self.config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(username='test', role='ADMIN',
                         email='test@testing.com')
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        """Closes the database session and drops all tables.
        """
        db.session.close()
        db.drop_all()
        self.app_context.pop()