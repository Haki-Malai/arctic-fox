from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses
from api import db
from api.models import Task, assignment
from api.schemas import TaskSchema, \
    DateTimePaginationSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

tasks = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
update_task_schema = TaskSchema(partial=True)


@tasks.route('/',)
@authenticate(token_auth)
@paginated_response(tasks_schema,
                    order_by=Task.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_tasks():
    """Get available task list
    This endpoint requires authentication and uses pagination.
    """
    return Task.query.filter_by(start_date=None)


@tasks.route('/', methods=['POST'])
@authenticate(token_auth)
@body(task_schema)
@response(task_schema, 201)
def post_task(args):
    """Create a new task
    This endpoint requires authentication.
    """
    task = Task(**args)
    task.assignee_id = token_auth.current_user().id
    db.session.add(task)
    db.session.commit()
    return task


@tasks.route('/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({403: 'Not allowed to view', 404: 'Task not found'})
def get_task(task_id):
    """Retrieve a task by id
    This endpoint requires authentication.
    """
    task = db.session.get(Task, task_id) or abort(404)
    if task not in token_auth.current_user().assigned_tasks or\
        task not in token_auth.current_user().assigneed_tasks and \
            task.start_date is None:
        abort(403)
    return task


@tasks.route('/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_task_schema)
@response(task_schema)
@other_responses({403: 'Not allowed to edit', 404: 'Task not found'})
def put_task(data, task_id):
    """Edit task information
    This endpoint requires authentication.
    """
    task = db.session.get(Task, task_id) or abort(404)
    if task not in token_auth.current_user().assigneed_tasks:
        abort(403)
    task.update(data)
    db.session.commit()
    return task


@tasks.route('/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, 204)
@other_responses({403: 'Not allowed to delete', 404: 'Task not found'})
def delete_task(task_id):
    """Edit task information
    This endpoint requires authentication.
    """
    task = db.session.get(Task, task_id) or abort(404)
    if task not in token_auth.current_user().assigneed_tasks:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    return {}


@tasks.route('/assigned')
@authenticate(token_auth)
@paginated_response(tasks_schema,
                    order_by=Task.timestamp,
                    pagination_schema=DateTimePaginationSchema)
def get_tasks_assigned():
    """Retrieve tasks assigned to authenticated user.
    This endpoint requires authentication and uses pagination.
    """
    return token_auth.current_user().assigned_tasks


@tasks.route('/assigned/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({404: 'Task not found',
    403: 'Not allowed to read'})
def get_task_assigned(task_id):
    """Read a assigned task
    This endpoint requires authentication.
    """
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    if task not in token_auth.current_user().assigned_tasks:
        abort(403)
    return task


@tasks.route('/assigned/<int:id>', methods=['POST'])
@authenticate(token_auth)
@response(EmptySchema, 201)
@other_responses({404: 'Task not found',
    405: 'Assign to self not allowed', 409: 'Already assigned'})
def post_task_assigned(task_id):
    """Assign authenticated user to task"""
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    if task.assignee == token_auth.current_user():
        abort(405)
    if task.start_date is not None:
        abort(409)
    task.start(token_auth.current_user().id)
    return {}


@tasks.route('/assigned/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_task_schema)
@response(task_schema, 202)
@other_responses({403: 'Not allowed to edit', 404: 'Task not found'})
def put_task_assigned(data, task_id):
    """Add input to task as assigned user"""
    task = db.session.get(Task, task_id) or abort(404)
    if task not in token_auth.current_user().assigned_tasks:
        abort(403)
    if 'input_data' not in data or len(data) > 1:
        abort(403)
    task.update(data)
    db.session.commit()
    return task


@tasks.route('/assigneed')
@authenticate(token_auth)
@paginated_response(tasks_schema,
                    order_by=Task.timestamp,
                    pagination_schema=DateTimePaginationSchema)
def get_tasks_assigneed():
    """Retrieve tasks assigned from authenticated user."""
    return token_auth.current_user().assigneed_tasks


@tasks.route('/assigneed/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({404: 'Task not found', 403: 'Not allowed to read'})
def get_task_assigneed(task_id):
    """Read a assigneed task"""
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    if task not in token_auth.current_user().assigneed_tasks:
        abort(403)
    return task


@tasks.route('/assigneed/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_task_schema)
@response(task_schema)
@other_responses({403: 'Not allowed to edit', 404: 'Task not found'})
def put_task_assigneed(data, task_id):
    """Edit task as task creator"""
    task = db.session.get(Task, task_id) or abort(404)
    if task not in token_auth.current_user().assigneed_tasks:
        abort(403)
    task.update(data)
    db.session.commit()
    return task