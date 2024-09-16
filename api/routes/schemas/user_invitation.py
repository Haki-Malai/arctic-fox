from marshmallow import validate
from marshmallow_enum import EnumField

from api import ma
from database.enums import Role


class UserInvitationSchema(ma.Schema):
    email = ma.String(required=True, validate=validate.Email())
    role = EnumField(Role)
