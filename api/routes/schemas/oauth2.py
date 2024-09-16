from api import ma


class OAuth2Schema(ma.Schema):
    code = ma.String(required=True)
    state = ma.String(required=True)
