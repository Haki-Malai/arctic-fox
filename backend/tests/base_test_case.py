import unittest
from api.app import create_app, db
from api.models import User


class BaseTestCase(unittest.TestCase):  # nosec

    username = 'username'
    password = 'password'

    def setUp(self):
        self.app = create_app('testing')
        self.email = self.app.config['MAIL_FOR_TEST_OR_DEBUG']
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.user = User(username=self.username,
                    email=self.email,
                    password=self.password)
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.app_context.pop()