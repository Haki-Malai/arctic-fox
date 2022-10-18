from flask import Blueprint, request, abort, current_app, url_for
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

from api.app import db
from api.auth import basic_auth, token_auth
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, EmptySchema

tokens = Blueprint('tokens', __name__)
token_schema = TokenSchema()


def token_response(token):
    return {
        'access_token': token.access_token,
        'refresh_token': token.refresh_token
        #if current_app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }, 200


@tokens.route('/tokens', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema)
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new access token"""
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # Keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@tokens.route('/tokens', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access token')
@other_responses({401: 'Invalid access token'})
def refresh(args):
    """Refresh an access token
    """
    access_token = args['access_token']
    refresh_token = args.get('refresh_token', request.cookies.get(
        'refresh_token'))
    if not access_token or not refresh_token:
        abort(401)
    token = User.verify_refresh_token(refresh_token, access_token)
    if not token:
        abort(401)
    token.expire()
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_response(new_token)


@tokens.route('/tokens', methods=['DELETE'])
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: 'Invalid access token'})
def revoke():
    """Revoke an access token"""
    access_token = request.headers['Authorization'].split()[1]
    token = Token.query.filter_by(access_token=access_token).first()
    if not token:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}


@tokens.route('/tokens/reset', methods=['POST'])
@body(PasswordResetRequestSchema)
@response(EmptySchema, status_code=204, description='Password reset email sent')
def reset(args):
    """Request a password reset token"""
    user = User.query.filter_by(email=args['email']).first()
    if user is not None:
        reset_token = user.generate_reset_token()
        reset_url = current_app.config['PASSWORD_RESET_URL'] + \
            '?token=' + reset_token
        send_email(args['email'], 'Reset Your Password', 'reset',
                   token=reset_token, url=reset_url)
    return {"test": "email_send (supposedly)"}
