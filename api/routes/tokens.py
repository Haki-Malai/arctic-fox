from flask import Blueprint, request, abort, current_app, url_for
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

from api import db
from api.auth import google_auth, token_auth
from api.token import Token
from api.schemas import TokenSchema, EmptySchema, OAuth2Schema
from database.models import User

from typing import Dict

bp = Blueprint('tokens', __name__)
token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


def token_response(token: Token) -> Dict:
    """Return the token as a response

    :param token: The token object

    :return: The token as a response
    """
    headers = {}
    headers['Set-Cookie'] = dump_cookie(
        'refresh_token', token.refresh_token,
        path=url_for('tokens.new'), secure=not current_app.debug,
        httponly=True, samesite='none')
    return {
        'access_token': token.access_token_jwt,
    }, 200, headers


@bp.route('/tokens', methods=['POST'])
@authenticate(google_auth)
@response(token_schema)
@other_responses({401: 'Invalid OAuth2 code or state'})
def new() -> Token:
    """Create new access and refresh tokens

    The refresh token is returned as a hardened cookie. A cookie should be
    used when the client is running in an insecure environment such as a web
    browser, and cannot adequately protect the refresh token against
    unauthorized access.
    """
    user = google_auth.current_user()
    if not user:
        abort(404, 'User does not exist.')
    token = user.generate_auth_token()
    Token.clean()
    return token_response(token)


@bp.route('/tokens', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access and refresh tokens')
@other_responses({401: 'Invalid access or refresh token'})
def refresh(data: dict) -> Token:
    """Refresh an access token

    The client has the ability to pass the refresh token in a `refresh_token`
    cookie. The access token must be passed in the body of the request.
    """
    access_token_jwt = data['access_token']
    refresh_token = request.cookies.get('refresh_token')
    if not access_token_jwt or not refresh_token:
        abort(401)
    token = User.verify_refresh_token(refresh_token, access_token_jwt)
    if not token:
        abort(401)
    token.expire()
    user = db.session.get(User, token.user_id)
    new_token = user.generate_auth_token()
    return token_response(new_token)


@bp.route('/tokens', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({400: 'Invalid access token'})
def revoke() -> Dict:
    """Revoke an access token"""
    access_token_jwt = request.headers['Authorization'].split()[1]
    token = Token.from_jwt(access_token_jwt)
    if not token:
        abort(400, 'Invalid access token')
    token.expire()
    return {}
