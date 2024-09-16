from marshmallow import validate

from api import ma
from database.models import Folder


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

    owner = ma.Nested('UserSchema', exclude=('folders',), dump_only=True)
    files = ma.Nested(
        'FileSchema', exclude=('folder',), many=True, dump_only=True)
