from api.schemas import StringPaginationSchema, PaginatedCollection
from functools import wraps
from apifairy import arguments, response
from sqlalchemy.sql.expression import desc


def paginated_response(schema, max_limit=25, order_by=None,
                       order_direction='asc',
                       pagination_schema=StringPaginationSchema):
    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            query = f(*args, **kwargs)
            if query is not None:
                if order_by is not None:
                    if order_direction == 'desc':
                        query = query.order_by(desc(order_by))
                    else:
                        query = query.order_by(order_by)

                count = query.count()
                limit = pagination.get('limit', max_limit)
                if limit > max_limit:
                    query = query.limit(max_limit)
                else:
                    query = query.limit(limit)

                data = query.all()
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