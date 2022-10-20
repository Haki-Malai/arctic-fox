from marshmallow import validate, validates, validates_schema, \
    ValidationError, post_dump
from api import ma, db
from api.auth import token_auth
from api.models import User, Post, Comment, Notification, Task

paginated_schema_cache = {}


class EmptySchema(ma.Schema):
    pass


class DateTimePaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)


class StringPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)


def PaginatedCollection(schema, pagination_schema=StringPaginationSchema):
    if schema in paginated_schema_cache:
        return paginated_schema_cache[schema]

    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True

        pagination = ma.Nested(pagination_schema)
        data = ma.Nested(schema, many=True)

    PaginatedSchema.__name__ = f'Paginated{schema.__class__.__name__}'
    paginated_schema_cache[schema] = PaginatedSchema
    return PaginatedSchema


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    username = ma.auto_field(required=True, validate=validate.Length(min=8, max=64))
    email = ma.auto_field(required=True,
                          validate=[validate.Email(), validate.Length(max=128)])
    password = ma.String(required=True, load_only=True,
                             validate=validate.Length(min=8, max=128))
    confirmed = ma.auto_field(dump_only=True)
    location = ma.auto_field(dump_only=True)
    avatar_hash = ma.auto_field(dump_only=True)
    member_since = ma.auto_field(dump_only=True)
    bitcoin_address = ma.auto_field()

    @validates('username')
    def validate_username(self, value):
        user = token_auth.current_user()
        old_username = user.username if user else None
        if value != old_username and \
                User.query.filter_by(username=value).first():
            raise ValidationError('Use a different username.')

    @validates('email')
    def validate_email(self, value):
        user = token_auth.current_user()
        old_email = user.email if user else None
        if value != old_email and \
                User.query.filter_by(email=value).first():
            raise ValidationError('Use a different email.')


class UpdateUserSchema(UserSchema):
    old_password = ma.String(load_only=True, validate=validate.Length(min=3))

    @validates('old_password')
    def validate_old_password(self, value):
        if not token_auth.current_user().verify_password(value):
            raise ValidationError('Password is incorrect')


class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String(required=True)


class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
        ordered = True

    id = ma.auto_field(dump_only=True)
    body = ma.auto_field(required=True,\
        validate=validate.Length(min=1, max=140))
    timestamp = ma.auto_field(dump_only=True)

    
class CommentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Comment
        ordered = True

    id = ma.auto_field()
    body = ma.auto_field(required=True,\
        validate=validate.Length(min=1, max=140))
    timestamp = ma.auto_field(dump_only=True) 
    post_id = ma.auto_field(required=True)

    @validates('post_id')
    def validate_old_password(self, value):
        try:
            int(value)
        except ValueError:
            raise ValueError(f'Post id must be an integer not {type(value)}')


class NotificationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Notification
        ordered = True

    id = ma.auto_field()
    body = ma.auto_field(required=True,\
        validate=validate.Length(min=1, max=140))
    read = ma.auto_field(dump_only=True)
    timestamp = ma.auto_field(dump_only=True) 
    post_id = ma.auto_field(dump_only=True)
    comment_id = ma.auto_field(dump_only=True)

    
class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Task
        ordered = True

    id = ma.auto_field()
    name = ma.auto_field(load_only=True,\
        validate=validate.Length(min=8, max=140))
    description = ma.auto_field(load_only=True,\
        validate=validate.Length(min=8, max=140))
    value = ma.auto_field()
    complete = ma.auto_field()
    timestamp = ma.auto_field(dump_only=True)
    start_date = ma.auto_field(dump_only=True)
    due_date = ma.auto_field()
    end_date = ma.auto_field(dump_only=True)
    last_update_date = ma.auto_field(dump_only=True)
    url = ma.auto_field()
    input_data = ma.auto_field()
    assignee_id = ma.auto_field()


class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String(required=True)
    refresh_token = ma.String()


class PasswordResetRequestSchema(ma.Schema):
    class Meta:
        ordered = True

    email = ma.String(required=True, validate=[validate.Length(max=120),
                                               validate.Email()])


class PasswordResetSchema(ma.Schema):
    class Meta:
        ordered = True

    token = ma.String(required=True)
    new_password = ma.String(required=True, validate=validate.Length(min=3))