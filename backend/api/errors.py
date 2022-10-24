from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError
from flask import jsonify

def register_error_handlers(app):
    """Register error handlers with the Flask application."""
    def http_error(error):
        return jsonify({
            'code': error.code,
            'message': error.name,
            'description': error.description,
        }), error.code

    def db_integrity_error(error):  # pragma: no cover
        return {
            'code': 400,
            'message': 'Database integrity error',
            'description': str(error.orig),
        }, 400

    def db_error(error):  # pragma: no cover
            return {
                'code': InternalServerError.code,
                'message': InternalServerError().name,
                'description': InternalServerError.description,
            }, 500

    app.register_error_handler(HTTPException, http_error)
    app.register_error_handler(IntegrityError, db_integrity_error)
    app.register_error_handler(SQLAlchemyError, db_error)