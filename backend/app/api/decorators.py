from functools import wraps
from flask import g
from .errors import error_response


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_functions(*args, **kwargs):
            if not g.current_user.can(permission):
                return error_response(403)
            return f(*args, **kwargs)
        return decorated_functions
    return decorator