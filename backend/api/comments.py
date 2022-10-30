from flask import Blueprint, abort
from api.models import Post, Comment
from api.schemas import CommentSchema, DateTimePaginationSchema
from api.auth import token_auth
from api.decorators import paginated_response
from apifairy import authenticate, body, response, other_responses
from api import db

comments = Blueprint('comments', __name__)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
update_comment_schema = CommentSchema(partial=True)


@comments.route('/')
@authenticate(token_auth)
@paginated_response(comments_schema,
                    order_by=Comment.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_comments():
    """Retrieve all comments.
    This endpoint requires authentication and uses pagination.
    """
    return Comment.query


@comments.route('/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(comment_schema)
@other_responses({404: 'Comment not found'})
def get_comment(comment_id):
    """Retrieve a comment by id
    This endpoint requires authentication.
    """
    return db.session.get(Comment, comment_id) or abort(404)


@comments.route('/', methods=['POST'])
@body(comment_schema)
@response(comment_schema, 201)
@other_responses({403: 'Permission denied'})
def post_comment(args):
    """Create a new comment
    This endpoint requires authentication.
    """
    user_id = token_auth.current_user()
    comment = Comment(user_id=user_id, **args)
    db.session.add(comment)
    db.session.commit()
    return comment

@comments.route('/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_comment_schema)
@response(comment_schema)
@other_responses({403: 'Not allowed to edit this comment',
                  404: 'Comment not found'})
def put_comment(data, comment_id):
    """Edit a comment
    This endpoint requires authentication.
    """
    comment = db.session.get(Comment, comment_id) or abort(404)
    if comment.user_id != token_auth.current_user().id:
        abort(403)
    comment.update(data)
    db.session.commit()
    return comment


@comments.route('/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the comment'})
def delete_comment(comment_id):
    """Delete a comment
    This endpoint requires authentication.
    """
    comment = db.session.get(Comment, comment_id) or abort(404)
    if comment.user_id != token_auth.current_user().id and \
        token_auth.current_user().can(Permission.MODERATE_COMMENTS):
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return '', 204