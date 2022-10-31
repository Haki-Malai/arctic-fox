from api.app import apifairy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError
from flask import jsonify, Blueprint

errors = Blueprint('errors', __name__)

def register_error_handlers(app):
    """Register error handlers with the Flask application."""

@errors.app_errorhandler(HTTPException)
def http_error(error):
    return jsonify({
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }), error.code


@errors.app_errorhandler(IntegrityError)
def db_integrity_error(error):  # pragma: no cover
    return jsonify({
        'code': 400,
        'message': 'Database integrity error',
        'description': str(error.orig),
    }), 400


@errors.app_errorhandler(SQLAlchemyError)
def db_error(error):  # pragma: no cover
    return jsonify({
        'code': InternalServerError.code,
        'message': InternalServerError().name,
        'description': InternalServerError.description,
    }), 500

@apifairy.error_handler
def validation_error(code, messages):  # pragma: no cover
    err_key = list(messages.keys())[0]
    return jsonify({
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages[err_key],
        'fields': [k for k in messages[err_key].keys()]
    }), code