from apifairy.decorators import other_responses
from flask import Blueprint, abort
from apifairy import authenticate, body, response

from api import db
from .schemas import UserSchema, UserInvitationSchema, EmptySchema
from api.auth import token_auth
from database.models import User
from database.enums import Role

from typing import Optional, List

bp = Blueprint('users', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@bp.route('/users', methods=['POST'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@body(UserInvitationSchema)
@response(user_schema, 201)
@other_responses({400: 'User already exists'})
def post(data: dict) -> Optional[User]:
    """Invite a user to the system
    Create a new user

    :roles: admin, moderator

    :param data: The user data to create

    :return: The new user
    """
    user = token_auth.current_user()
    new_user = user.invite(data.get('email'), data.get('role')) \
        or abort(400, 'User already exists')
    return new_user


@bp.route('/users/<int:id>', methods=['DELETE'])
@authenticate(token_auth, role=[Role.ADMIN.name])
@response(EmptySchema, 204)
@other_responses({404: 'User not found'})
def delete(id: int) -> dict:
    """Delete a user

    :roles: admin

    :param id: The id of the user to delete

    :return: Empty response
    """
    user = db.session.get(User, id) or abort(404)
    db.session.delete(user)
    db.session.commit()
    return {}


@bp.route('/users/<int:id>', methods=['PUT'])
@body(user_schema)
@response(user_schema)
@authenticate(token_auth, role=[Role.ADMIN.name])
@other_responses({404: 'User not found'})
def put(data: dict, id: int) -> Optional[User]:
    """Edit a user
    :roles: admin

    :param data: The user data to update
    :param id: The id of the user to edit

    :return: The updated user
    """
    user = db.session.get(User, id) or abort(404)
    user.update(data)
    db.session.commit()
    return user


@bp.route('/users', methods=['GET'])
@authenticate(token_auth)
@response(users_schema)
def all() -> List[User]:
    """Retrieve all users

    :return: All users
    """
    return db.session.scalars(User.select())


@bp.route('/users/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(id: int) -> Optional[User]:
    """Retrieve a user by id

    :param id: The id of the user to retrieve

    :return: The user
    """
    return db.session.get(User, id) or abort(404)


@bp.route('/me', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
def me() -> User:
    """Retrieve the authenticated user

    :return: The authenticated user
    """
    return token_auth.current_user()
