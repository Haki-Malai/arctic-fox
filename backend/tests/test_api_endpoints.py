from flask import url_for
from tests.base_test_case import BaseTestCase
from flask import request

class ApiEndpointTestCase(BaseTestCase):

    def test_api_endpoints(self, case):
        response = case.call_asgi(self.app)
        case.validate_response(response)