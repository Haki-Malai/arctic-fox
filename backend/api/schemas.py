from marshmallow import validate, validates, validates_schema, \
    ValidationError, post_dump
from api import ma, db
from api.auth import token_auth
from api.models import User, Post

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

    PaginatedSchema.__name__ = 'Paginated{}'.format(schema.__class__.__name__)
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

class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        ordered = True
        load_instance = True
        include_fk = True
        incluce_relationships = True


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