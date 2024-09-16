from marshmallow import validate

from api import ma, aws_wrapper
from database.models import File


class FileSchema(ma.SQLAlchemySchema):
    class Meta:
        model = File
        ordered = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    filename = ma.auto_field(validate=validate.Length(max=64))
    mimetype = ma.auto_field()
    description = ma.auto_field(validate=validate.Length(max=280))
    processed = ma.auto_field(dump_only=True)
    dominant_color = ma.auto_field(dump_only=True)
    error = ma.auto_field(dump_only=True)
    created_by = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    folder_id = ma.auto_field()
    preview_url = ma.Method('get_preview_url', dump_only=True)

    owner = ma.Nested('UserSchema', exclude=('files',), dump_only=True)
    folder = ma.Nested('FolderSchema', exclude=('files',), dump_only=True)

    def get_preview_url(self, obj: dict) -> str:
        """Generate a URL for previewing the file if it is stored in S3.
        
        :return: URL for previewing the file
        """
        return aws_wrapper.generate_presigned_url(obj.filename)
