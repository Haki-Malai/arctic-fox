from flask import Blueprint, request, abort, current_app, url_for
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

from api.app import db
from api.auth import basic_auth, token_auth
from api.models import User
from api.schemas import TokenSchema#, PasswordResetRequestSchema, \
#    PasswordResetSchema, EmptySchema

tokens = Blueprint('tokens', __name__)
token_schema = TokenSchema()


def token_response(token):
    return {
        'access_token': token
    }, 200

    
@tokens.route('/tokens', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema)
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new access token"""
    user = basic_auth.current_user()
    token = user.generate_access_token()
    return token_response(token)


@tokens.route('/tokens', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access token')
@other_responses({401: 'Invalid access token'})
def refresh(args):
    """Refresh an access token
    """
    access_token = args['access_token']
    if not access_token:
        abort(401)
    user = User.verify_access_token(access_token)
    if not user:
        abort(401)
    new_token = user.generate_access_token() if user else None
    return token_response(new_token)
    

@tokens.route('/tokens', methods=['DELETE'])
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: 'Invalid access token'})
def revoke():
    """Revoke an access token"""
    access_token = request.headers['Authorization'].split()[1]
    if not access_token:
        abort(401)
    user = User.verify_access_token(access_token)
    if not user:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}
