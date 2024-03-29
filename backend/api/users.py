from api import db
from api.models import User, Post, Comment, Notification
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema,\
    DateTimePaginationSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.posts import posts_schema
from api.comments import comments_schema
from api.notifications import notifications_schema
from apifairy import authenticate, body, response
from apifairy.decorators import other_responses
from flask import Blueprint, abort

users = Blueprint('users', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema()


@users.route('/')
@authenticate(token_auth)
@paginated_response(users_schema)
def get_users():
    """Retrieve all users
    This is a paginated endpoint. You can pass query
    parameters to paginate the results.
    """
    return User.query


@users.route('/', methods=['POST'])
@body(user_schema)
@response(user_schema)
@other_responses({400: 'Bad Request', 422: 'Unprocessable Entity'})
def post_user(args):
    """Register a new user
    Must provide required fields.
    """
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    return user


@users.route('/<int:user_id>')
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get_user(user_id):
    """Retrieve a user by id
    This endpoint requires authentication.
    """
    return db.session.get(User, user_id) or abort(404)


@users.route('/<username>')
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get_user_by_username(username):
    """Retrieve a user by username
    This endpoint requires authentication.
    """
    return User.query.filter_by(username=username).first() or abort(404)


@users.route('/me')
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user
    This endpoint requires authentication.
    """
    return token_auth.current_user()


@users.route('/me', methods=['PUT'])
@authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def put(data):
    """Edit user information
    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
        abort(400)
    user.update(data)
    db.session.commit()
    return user


@users.route('/me/following')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def my_following():
    """Retrieve the users the logged in user is following
    This endpoint requires authentication and is paginated.
    """
    user = token_auth.current_user()
    return user.following


@users.route('/me/followers')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def my_followers():
    """Retrieve the followers of the logged in user
    This endpoint requires authentication and is paginated.
    """
    user = token_auth.current_user()
    return user.followers


@users.route('/me/following/<int:user_id>')
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User is followed.')
@other_responses({404: 'User is not followed'})
def is_followed(user_id):
    """Check if a user is followed
    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    followed_user = db.session.get(User, user_id) or abort(404)
    if not user.is_following(followed_user):
        abort(404)
    return {}


@users.route('/me/following/<int:user_id>', methods=['POST'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User followed successfully.')
@other_responses({404: 'User not found', 409: 'User already followed.'})
def follow(user_id):
    """Follow a user
    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    followed_user = db.session.get(User, user_id) or abort(404)
    if user.is_following(followed_user):
        abort(409)
    user.follow(followed_user)
    db.session.commit()
    return {}


@users.route('/me/following/<int:user_id>', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User unfollowed successfully.')
@other_responses({404: 'User not found', 409: 'User is not followed.'})
def unfollow(user_id):
    """Unfollow a user
    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    unfollowed_user = db.session.get(User, user_id) or abort(404)
    if not user.is_following(unfollowed_user):
        abort(409)
    user.unfollow(unfollowed_user)
    db.session.commit()
    return {}


@users.route('/following/<int:user_id>')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
@other_responses({404: 'User not found'})
def following(user_id):
    """Retrieve the users this user is following
    This endpoint requires authentication.
    """
    user = db.session.get(User, user_id) or abort(404)
    return user.following


@users.route('/followers/<int:user_id>')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
@other_responses({404: 'User not found'})
def followers(user_id):
    """Retrieve the followers of an user
    This endpoint requires authentication and uses pagination.
    """
    user = db.session.get(User, user_id) or abort(404)
    return user.followers


@users.route('/posts/<int:user_id>')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(posts_schema,
                    order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user_posts(user_id):
    """Retrieve the posts of an user
    This endpoint requires authentication and uses pagination"""
    user = db.session.get(User, user_id) or abort(404)
    return user.posts


@users.route('/comments')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(comments_schema,
                    order_by=Comment.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user_comments():
    """Retrieve user's comments
    This endpoint requires authentication and uses pagination
    """
    return token_auth.current_user().comments


@users.route('/notifications')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(notifications_schema,
                    order_by=Notification.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user_notifications():
    """Retrieve user's notifications
    This endpoint requires authentication and uses pagination
    """
    return token_auth.current_user().notifications