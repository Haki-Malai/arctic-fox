from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses
from api import db
from api.models import User, Post, Permission
from api.schemas import PostSchema, DateTimePaginationSchema
from api.auth import token_auth
from api.decorators import paginated_response

posts = Blueprint('posts', __name__)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
update_post_schema = PostSchema(partial=True)


@posts.route('/')
@authenticate(token_auth)
@paginated_response(posts_schema,
                    order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all posts."""
    return Post.query


@posts.route('/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(post_schema)
@other_responses({404: 'Post not found'})
def get(id):
    """Retrieve a post by id"""
    return db.session.get(Post, id) or abort(404)


@posts.route('/', methods=['POST'])
@body(post_schema)
@response(post_schema, 201)
@other_responses({403: 'Permission denied'})
def new(args):
    """Create a new post"""
    user = token_auth.current_user()
    post = Post(user_id=user.id, **args)
    db.session.add(post)
    db.session.commit()
    return post

@posts.route('/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_post_schema)
@response(post_schema)
@other_responses({403: 'Not allowed to edit this post',
                  404: 'Post not found'})
def put(data, id):
    """Edit a post"""
    post = db.session.get(Post, id) or abort(404)
    if post.user_id != token_auth.current_user().id and \
        token_auth.current_user().can(Permission.MODERATE_COMMENTS):
        abort(403)
    post.update(data)
    db.session.commit()
    return post


@posts.route('/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the post'})
def delete(id):
    """Delete a post"""
    post = db.session.get(Post, id) or abort(404)
    if post.user_id != token_auth.current_user().id and \
        token_auth.current_user().can(Permission.MODERATE_COMMENTS):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return '', 204


@posts.route('/user/<int:id>')
@authenticate(token_auth)
@other_responses({404: 'User not found'})
@paginated_response(posts_schema,
                    order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_user(id):
    """Retrieve an user's posts"""
    return Post.query.filter_by(user_id=id)