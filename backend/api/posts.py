from api import db
from api.models import Post, Comment
from api.schemas import PostSchema, DateTimePaginationSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.comments import comments_schema
from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses

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
def get_posts():
    """Retrieve all posts.
    This endpoint requires authentication and uses pagination.
    """
    return Post.query


@posts.route('/', methods=['POST'])
@body(post_schema)
@response(post_schema, 201)
@other_responses({403: 'Permission denied'})
def post_post(args):
    """Create a new post
    This endpoint requires authentication.
    """
    user = token_auth.current_user()
    post = Post(user_id=user.id, **args)
    db.session.add(post)
    db.session.commit()
    return post


@posts.route('/<int:id>')
@authenticate(token_auth)
@response(post_schema)
@other_responses({404: 'Post not found'})
def get_post(post_id):
    """Retrieve a post by id
    This endpoint requires authentication.
    """
    return db.session.get(Post, post_id) or abort(404)

@posts.route('/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_post_schema)
@response(post_schema)
@other_responses({403: 'Not allowed to edit this post',
                  404: 'Post not found'})
def put_post(data, post_id):
    """Edit a post
    This endpoint requires authentication.
    """
    post = db.session.get(Post, post_id) or abort(404)
    if post.user_id != token_auth.current_user().id:
        abort(403)
    post.update(data)
    db.session.commit()
    return post


@posts.route('/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the post'})
def delete_post(post_id):
    """Delete a post
    This endpoint requires authentication.
    """
    post = db.session.get(Post, post_id) or abort(404)
    if post.user_id != token_auth.current_user().id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return '', 204


@posts.route('/comments/<int:id>')
@authenticate(token_auth)
@other_responses({404: 'Post not found'})
@paginated_response(comments_schema,
                    order_by=Comment.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_post_comments(post_id):
    """Retrieve the comments of a post
    This endpoint requires authentication and uses pagination.
    """
    return Comment.query.filter_by(post_id=post_id) if db.session.get(Post, post_id) \
        else abort(404)