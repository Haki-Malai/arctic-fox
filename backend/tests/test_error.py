from api.models import User, Role, Post, Comment
import unittest
import json
import re
from base64 import b64encode
from api.app import create_app, db
from werkzeug.http import HTTP_STATUS_CODES


class ErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self, status_code=404):
        response = self.client.get('/wrong/url',
                                   headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == status_code)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['error'] == HTTP_STATUS_CODES.get(status_code, 'Unknown error'))
    
    def test_no_auth(self):
        response = self.client.get('/api/posts', \
            content_type='application/json')
        self.assertTrue(response.status_code == 401)
