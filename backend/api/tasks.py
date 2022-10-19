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


@tasks.route('/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({403: 'Not allowed to view', 404: 'Task not found'})
def get(id):
    task = db.session.get(Task, id) or abort(404)
    if token_auth.current_user() not in [task.assigned or task.assignee]:
        abort(403)
    return task