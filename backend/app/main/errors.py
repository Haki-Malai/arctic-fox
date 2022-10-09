from flask import make_response, jsonify
from . import main

@main.app_errorhandler(404)
def not_found(e):
    return make_response(
        jsonify(
            success=False
        ), 404
    )

@main.app_errorhandler(500)
def server_error(e):
    return make_response(
        jsonify(
            success=False
        ), 500
    )