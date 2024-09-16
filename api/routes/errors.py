from flask import Blueprint, current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError

from api.app import apifairy

bp = Blueprint('errors', __name__)


@bp.app_errorhandler(HTTPException)
def http_error(error: HTTPException) -> tuple:
    """Handle HTTP errors

    :param error: The HTTP error

    :return: The response tuple
    """
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }, error.code


@bp.app_errorhandler(IntegrityError)
def sqlalchemy_integrity_error(error: IntegrityError) -> tuple:
    """Handle SQLAlchemy integrity errors

    :param error: The SQLAlchemy integrity error

    :return: The response tuple
    """
    return {
        'code': 400,
        'message': 'Database integrity error',
        'description': str(error.orig),
    }, 400


@bp.app_errorhandler(SQLAlchemyError)
def sqlalchemy_error(error: SQLAlchemyError) -> tuple:
    """Handle SQLAlchemy errors

    :param error: The SQLAlchemy error

    :return: The response tuple
    """
    if current_app.config['DEBUG'] is True:
        return {
            'code': InternalServerError.code,
            'message': 'Database error',
            'description': str(error),
        }, 500
    else:
        return {
            'code': InternalServerError.code,
            'message': InternalServerError().name,
            'description': InternalServerError.description,
        }, 500


@apifairy.error_handler
def validation_error(code: int, messages: dict) -> tuple:
    """Handle validation errors

    :param code: The status code
    :param messages: The validation error messages

    :return: The response tuple
    """
    return {
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages,
    }, code
