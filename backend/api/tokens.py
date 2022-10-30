from api.app import db
from api.auth import basic_auth, token_auth
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetSchema, EmptySchema,\
    ConfirmationSchema, PasswordResetRequestSchema
from api.email import send_email
from flask import Blueprint, request, abort, current_app, url_for
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

tokens = Blueprint('tokens', __name__)
token_schema = TokenSchema()


def token_response(token):
    headers = {}
    if current_app.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'strict'
        if current_app.config['USE_CORS']:  # pragma: no branch
            samesite = 'none' if not current_app.debug else 'lax'
        headers['Set-Cookie'] = dump_cookie(
            'refresh_token', token.refresh_token,
            path=url_for('tokens.new'), secure=not current_app.debug,
            httponly=True, samesite=samesite)
    return {
        'access_token': token.access_token,
        'refresh_token': token.refresh_token
        if current_app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }, 200, headers

@tokens.route('/')
@authenticate(token_auth)
@response(EmptySchema, status_code=200)
def check():
    """Check if the current user is authenticated
    """
    return {}


@tokens.route('/', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema, status_code=200, description='Token Accepted')
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new access and refresh tokens
    Creates a new access token for the authenticated user. The access token
    will be valid for X minutes. A refresh token will be returned that can be
    used to get a new access token without re-authenticating the user. The
    refresh token is valid for X days.
    """
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # Keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@tokens.route('/', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access token')
@other_responses({401: 'Invalid access token'})
def refresh(args):
    """Refresh an access token
    Refreshes an access token. The refresh token must be passed in a cookie
    or the body. The access token must be passed in the body of the request.
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


@tokens.route('/', methods=['DELETE'])
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: 'Invalid access token'})
def revoke():
    """Revoke an access token
    Revokes an access token. The access token must be passed in the headers
    as a Bearer Token.
    """
    access_token = request.headers['Authorization'].split()[1]
    token = Token.query.filter_by(access_token=access_token).first()
    if not token:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}


@tokens.route('/reset', methods=['POST'])
@body(PasswordResetRequestSchema)
@response(EmptySchema, status_code=204,
    description='Password reset email sent')
@other_responses({400: 'Invalid email address'})
def reset(args):
    """Request a password reset token
    Requests a password reset token. The email address of the user must be
    passed in the body of the request.
    """
    user = User.query.filter_by(email=args['email']).first()
    if user is None:
        abort(400)
    reset_token = user.generate_reset_token()
    reset_url = f'{request.host}/api/reset?token={reset_token}'
    send_email(args['email'], 'Reset Your Password', 'reset',
                token=reset_token, url=reset_url)
    return {}


@tokens.route('/reset', methods=['PUT'])
@body(PasswordResetSchema)
@response(EmptySchema, status_code=204,
          description='Password reset successful')
@other_responses({400: 'Invalid reset token'})
def password_reset(args):
    """Reset a user password
    Resets a user password. The reset token and new password must be passed
    in the body of the request.
    """
    user = User.verify_reset_token(args['token'])
    if user is None:
        abort(400)
    user.password = args['new_password']
    user.ping()
    db.session.commit()
    return {}


@tokens.route('/confirm/<token>')
@response(EmptySchema, status_code=204,
          description='Account confirmation successful')
@other_responses({400: 'Invalid confirm token'})
def user_confirm(token):
    """Confirm a user account
    Confirms a user account. The confirm token must be passed in the URL.
    """
    user = User.verify_confirm_token(token)
    if user is None:
        abort(400)
    user.confirmed = True
    user.ping()
    db.session.commit()
    return {}