import requests
from flask import current_app, abort
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import Unauthorized, Forbidden
from jwt import DecodeError

from google.oauth2 import id_token
from google.auth.transport import requests

from api.app import db
from api.models import User

from typing import Tuple

google_auth = HTTPTokenAuth(scheme='Bearer')
token_auth = HTTPTokenAuth(scheme='Bearer')


@google_auth.verify_token
def verify_google_token(credential:str) -> User|None:
    """Exchange OAuth2 credential code for access token and verify it.

    :param credential: The OAuth2 credential value.

    :return: The user associated with the exchanged access token.
    """
    if current_app.config['DISABLE_AUTH']:
        return db.session.scalar(User.select())

    if credential:
        idinfo = id_token.verify_oauth2_token(
            credential, requests.Request(), current_app.config['GOOGLE_CLIENT_ID'])

        if 'email' in idinfo:
            user = db.session.scalar(
                User.select().where(User.email == idinfo['email'])) or abort(401)

            user.activate(idinfo)
            db.session.commit()

            return user


@token_auth.verify_token
def verify_token(access_token: str) -> User|None:
    """Verify the access token.

    :param access_token: The access token.

    :return: The user associated with the access token.
    """
    if current_app.config['DISABLE_AUTH']:
        return db.session.scalar(User.select())
    if access_token:
        try:
            return User.verify_access_token(access_token)
        except DecodeError:
            abort(401)


@token_auth.get_user_roles
def get_user_roles(user: User) -> str:
    """Return the user's role.

    :param user: The user.

    :return: The user's role.
    """
    return user.role.name


@token_auth.error_handler
def token_auth_error(status: int=401) -> tuple[dict[int, str, str], int]:
    """Return the error response for the token auth error.

    :param status: The status code.

    :return: The error response.
    """
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }, error.code
