from marshmallow import validate
from marshmallow_enum import EnumField

from api import ma
from api.models import User, Folder, File
from api.enums import Role

paginated_schema_cache = {}


class EmptySchema(ma.Schema):
    pass


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(dump_only=True)
    email = ma.auto_field(required=True, dump_only=True)
    username = ma.auto_field(dump_only=True)
    avatar_url = ma.auto_field(dump_only=True)
    activated = ma.auto_field(dump_only=True)
    role = EnumField(Role)
    created_at = ma.auto_field(dump_only=True)

    folders = ma.Nested('FolderSchema', exclude=('owner', 'files'), many=True, dump_only=True)
    files = ma.Nested('FileSchema', exclude=('owner', 'folder'), many=True, dump_only=True)


class UserInvitationSchema(ma.Schema):
    email = ma.String(required=True, validate=validate.Email())
    role = EnumField(Role)


class FolderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Folder
        ordered = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(validate=validate.Length(max=64))
    description = ma.auto_field(validate=validate.Length(max=280))
    created_by = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)

    owner = ma.Nested(UserSchema, exclude=('folders',), dump_only=True)
    files = ma.Nested('FileSchema', exclude=('folder',), many=True, dump_only=True)


class PresignedFieldsSchema(ma.Schema):
    class Meta:
        ordered = True

    key = ma.String(required=True)
    AWSAccessKeyId = ma.String(required=True)
    policy = ma.String(required=True)
    signature = ma.String(required=True)


class PresignedPostSchema(ma.Schema):
    class Meta:
        ordered = True

    filename = ma.String(load_only=True)
    url = ma.String(dump_only=True)
    fields = ma.Nested(PresignedFieldsSchema, dump_only=True)


class FileSchema(ma.SQLAlchemySchema):
    class Meta:
        model = File
        ordered = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    filename = ma.auto_field(validate=validate.Length(max=64))
    mimetype = ma.auto_field(dump_only=True)
    description = ma.auto_field(validate=validate.Length(max=280))
    processed = ma.auto_field(dump_only=True)
    dominant_color = ma.auto_field(dump_only=True)
    error = ma.auto_field(dump_only=True)
    created_by = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)

    owner = ma.Nested(UserSchema, exclude=('files',), dump_only=True)
    folder = ma.Nested(FolderSchema, exclude=('files',), dump_only=True)


class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String(required=True)


class OAuth2Schema(ma.Schema):
    code = ma.String(required=True)
    state = ma.String(required=True)
