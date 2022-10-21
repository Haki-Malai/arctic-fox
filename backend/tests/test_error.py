import json
from base64 import b64encode
from werkzeug.http import HTTP_STATUS_CODES
from tests.base_test_case import BaseTestCase


class ErrorTestCase(BaseTestCase):
    def get_api_headers(self):
        return {
            'Authorization': 'Basic ' + b64encode(
                (self.username + ':' + self.password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get('/wrong/url',
                headers=self.get_api_headers())
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['error'] == HTTP_STATUS_CODES.get(404, 'Unknown error'))
    
    def test_no_auth(self):
        response = self.client.get('/api/posts', \
            content_type='application/json')
        self.assertTrue(response.status_code == 401)
