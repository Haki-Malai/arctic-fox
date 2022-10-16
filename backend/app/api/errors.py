from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from app.exceptions import ValidationError
from . import api


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])

