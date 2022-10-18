from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses
from api import db
from api.models import User, Post
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import PostSchema
from api.schemas import DateTimePaginationSchema

posts = Blueprint('posts', __name__)
post_schema = PostSchema(many=True)


@posts.route('/')
@authenticate(token_auth)
@paginated_response(post_schema,
                    order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all posts."""
    return Post.query


#@api.route('/posts', methods=['POST'])
#@permission_required(Permission.WRITE_ARTICLES)
#def new_posts():
    #post = Post.from_json(request.json)
    #post.author = g.current_user
    #db.session.add(post)
    #db.session.commit()
    #return jsonify(post.to_json()), 201, \
        #{'Location': url_for('api.get_post', id=post.id, _external=True)}

#@api.route('/posts/<int:id>', methods=['PUT'])
#@permission_required(Permission.WRITE_ARTICLES)
#def edit_post(id):
    #post = Post.query.get_or_404(id)
    #if g.current_user != post.author and \
            #not g.current_user.can(Permission.ADMIN):
        #return error_response(403)
    #post.body = request.json.get('body', post.body)
    #db.session.add(post)
    #db.session.commit()
    #return jsonify(post.to_json())