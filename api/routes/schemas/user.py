from marshmallow import validate
from marshmallow_enum import EnumField

from api import ma
from database.models import User
from database.enums import Role

paginated_schema_cache: dict = {}


class EmptySchema(ma.Schema):
    pass


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(dump_only=True)
    email = ma.auto_field(required=True, dump_only=True,
                          validate=validate.Email(error='Invalid email format.'))
    username = ma.auto_field(dump_only=True)
    avatar_url = ma.auto_field(dump_only=True)
    activated = ma.auto_field(dump_only=True)
    role = EnumField(Role)
    created_at = ma.auto_field(dump_only=True)

    folders = ma.Nested(
        'FolderSchema', exclude=('owner', 'files'), many=True, dump_only=True)
    files = ma.Nested(
        'FileSchema', exclude=('owner', 'folder'), many=True, dump_only=True)
