from flask import Blueprint
from apifairy import response

from api.schemas import EmptySchema

bp = Blueprint('health', __name__)

@bp.route('/health')
@response(EmptySchema, 200)
def health_check():
    """Health check endpoint"""
    return ''
