from tests.base_test_case import BaseTestCase


class BaseTestCase(BaseTestCase):
    def test_app_exists(self):
        self.assertFalse(self.app is None)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['FLASK_RUN_PORT'] == 5001)