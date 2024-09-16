from api import ma


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
