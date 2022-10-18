from api.errors.handlers import error_response
from api.models import User, Permission
from api.app import db
from flask import current_app, abort
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')


@basic_auth.verify_password
def verify_password(username, password):
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User.query.filter_by(email=username).first()
        if user and user.verify_password(password):
            return user


@basic_auth.error_handler
def auth_error(status_code=401):
    return abort(status_code)


@token_auth.verify_token
def verify_token(access_token):
    if access_token:
        return User.verify_access_token(access_token)

        
@token_auth.error_handler
def token_error(status_code=401):
    return abort(status_code)

    
#@token_auth.get_user_roles
#def get_user_roles(user):
    #return user.get_roles()