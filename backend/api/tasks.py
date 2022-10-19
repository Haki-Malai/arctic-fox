from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses
from api import db
from api.models import Task
from api.schemas import TokenSchema, TaskSchema, \
    DateTimePaginationSchema
from api.auth import token_auth
from api.decorators import paginated_response

tasks = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


@tasks.route('/')
@authenticate(token_auth)
@paginated_response(tasks_schema,
                    order_by=Task.timestamp,
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve tasks from authenticated user."""
    return token_auth.current_user().get_tasks()