from api import db
from api.models import User, Post, Comment, Notification, Task
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema,\
    CommentSchema, PostSchema, DateTimePaginationSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.posts import posts_schema
from api.comments import comments_schema
from api.notifications import notifications_schema
from api.tasks import tasks_schema
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
def all():
    """Retrieve all users

    This is a paginated endpoint. You can pass the following query
    parameters to paginate the results:

    - `page`: the page number to retrieve (default: 1)
    - `max_limit`: the number of items per page (default: 25)
    - `order_by`: the field to order the results by (default: None)
    - `order_direction`: the direction to order the results by (default: asc)
    """
    return User.query


@users.route('/', methods=['POST'])
@body(user_schema)
@response(user_schema)
@other_responses({400: 'Bad Request', 422: 'Unprocessable Entity'})
def new(args):
    """Register a new user

    The following fields are required:
    - `username`: the username for the user
    - `email`: the email address for the user
    - `password`: the password for the user
    """
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    return user


@users.route('/<int:id>')
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(id):
    """Retrieve a user by id

    This endpoint requires authentication.
    """
    return db.session.get(User, id) or abort(404)


@users.route('/<username>')
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get_by_username(username):
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


@users.route('/me/following/<int:id>')
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User is followed.')
@other_responses({404: 'User is not followed'})
def is_followed(id):
    """Check if a user is followed

    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    followed_user = db.session.get(User, id) or abort(404)
    if not user.is_following(followed_user):
        abort(404)
    return {}


@users.route('/me/following/<int:id>', methods=['POST'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User followed successfully.')
@other_responses({404: 'User not found', 409: 'User already followed.'})
def follow(id):
    """Follow a user

    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    followed_user = db.session.get(User, id) or abort(404)
    if user.is_following(followed_user):
        abort(409)
    user.follow(followed_user)
    db.session.commit()
    return {}


@users.route('/me/following/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User unfollowed successfully.')
@other_responses({404: 'User not found', 409: 'User is not followed.'})
def unfollow(id):
    """Unfollow a user

    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    unfollowed_user = db.session.get(User, id) or abort(404)
    if not user.is_following(unfollowed_user):
        abort(409)
    user.unfollow(unfollowed_user)
    db.session.commit()
    return {}


@users.route('/following/<int:id>')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
@other_responses({404: 'User not found'})
def following(id):
    """Retrieve the users this user is following

    This endpoint requires authentication.
    """
    user = db.session.get(User, id) or abort(404)
    return user.following


@users.route('/followers/<int:id>')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
@other_responses({404: 'User not found'})
def followers(id):
    """Retrieve the followers of the user

    This endpoint requires authentication and uses pagination.
    """
    user = db.session.get(User, id) or abort(404)
    return user.followers


@users.route('/posts/<int:id>')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(posts_schema,
                    order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user_posts(id):
    """Retrieve the posts of an user

    This endpoint requires authentication and uses pagination"""
    return token_auth.current_user().posts


@users.route('/comments')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(comments_schema,
                    order_by=Comment.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user_comments():
    """Retrieve the comments of an user

    This endpoint requires authentication and uses pagination"""
    return token_auth.current_user().comments


@users.route('/notifications')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(notifications_schema,
                    order_by=Notification.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user_notifications():
    """Retrieve the notifications of an user

    This endpoint requires authentication and uses pagination"""
    return token_auth.current_user().notifications