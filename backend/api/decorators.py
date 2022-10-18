from functools import wraps
from flask import abort
from apifairy import arguments, response
from sqlalchemy.sql.expression import desc
from api.app import db
from api.schemas import StringPaginationSchema, PaginatedCollection
from .models import Permission


def paginated_response(schema, max_limit=25, order_by=None,
                       order_direction='asc',
                       pagination_schema=StringPaginationSchema):
    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            select_query = f(*args, **kwargs)
            if select_query is not None:
                if order_by is not None:
                    if order_direction == 'desc':
                        select_query = select_query.order_by(desc(order_by))
                    else: 
                        select_query = select_query.order_by(order_by)

                count = select_query.count()
                limit = pagination.get('limit', max_limit)
                if limit > max_limit:
                    limit = max_limit
                    select_query = select_query.limit(limit)
                    select_query = query.filter(order_condition)

                data = select_query.all()
                return {
                    'data': data,
                    'pagination': {
                        'limit': limit,
                        'count': len(data),
                        'total': count,
                    }
                }

                # wrap with APIFairy's arguments and response decorators
        return arguments(pagination_schema)(response(PaginatedCollection(
            schema, pagination_schema=pagination_schema))(paginate))

    return inner

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)