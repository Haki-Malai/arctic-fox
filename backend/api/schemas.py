from marshmallow import validate, validates, ValidationError
import requests
from api import ma, db
from api.auth import token_auth
from api.models import User, Post, Comment, Notification, Task, assignment

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
    page = ma.Integer()
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

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True)
    email = ma.auto_field(required=True)
    password = ma.String(required=True, load_only=True,
                             validate=validate.Length(min=8, max=128))
    confirmed = ma.auto_field(dump_only=True)
    location = ma.auto_field(dump_only=True)
    avatar = ma.auto_field(dump_only=True)
    member_since = ma.auto_field(dump_only=True)
    bitcoin_address = ma.auto_field()

    @validates('username')
    def validate_username(self, username):
        if User.query.filter_by(username=username).first():
            raise ValidationError('Use a different username.')
        if not username.isalnum():
            raise ValidationError('Username must be alphanumeric.')
        if len(username) < 8:
            raise ValidationError('Username must be at least 8 characters long.')
        if len(username) > 64:
            raise ValidationError('Username must be at most 64 characters long.')

    @validates('email')
    def validate_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Use a different email.')
        if not validate.Email()(value):
            raise ValidationError('Email is not valid.')
        if len(value) > 64:
            raise ValidationError('Email must be at most 64 characters long.')

    @validates('password')
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if len(value) > 128:
            raise ValidationError('Password must be at most 128 characters long.')
        if not any(char.isdigit() for char in value) or \
            not any(char.isupper() for char in value) or \
            not any(char.islower() for char in value):
            raise ValidationError('Password must contain at least one uppercase, '
                                  'one lowercase and one digit.')


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
    refresh_token = ma.String()


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
    txid = ma.auto_field(required=True)
    transaction_status = ma.Integer(dump_only=True)
    transaction_amount = ma.Float(dump_only=True)

    @validates('txid')
    def validate_txid(self, txid):
        res = requests.get('https://api.blockcypher.com/v1/btc/main/txs/' + txid)
        if res.status_code != 200:
            raise ValidationError('Invalid transaction id')
        assigned_id = assignment.query.filter_by(task_id = self.id).first()
        user = db.session.get(User, assigned_id)
        if user.bitcoin_address not in res.json()['addresses']:
            raise ValidationError('Transaction does not match assigned user')


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

    
class ConfirmationSchema(ma.Schema):
    
    token = ma.String(required=True)