from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses
from api import db
from api.models import User, Task, assignment
from api.schemas import TokenSchema, TaskSchema, \
    DateTimePaginationSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

tasks = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
update_task_schema = TaskSchema(partial=True)
empty_schema = EmptySchema()


@tasks.route('/',)
@authenticate(token_auth)
@paginated_response(tasks_schema,
                    order_by=Task.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Get available task list"""
    return Task.query.filter_by(start_date=None)


@tasks.route('/', methods=['POST'])
@authenticate(token_auth)
@body(task_schema)
@response(task_schema, 201)
def new(args):
    """Create a new task"""
    task = Task(**args)
    task.assignee_id = token_auth.current_user().id
    db.session.add(task)
    db.session.commit()
    return task


@tasks.route('/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({403: 'Not allowed to view', 404: 'Task not found'})
def get(id):
    """Retrieve a task by id"""
    task = db.session.get(Task, id) or abort(404)
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
def put(data, id):
    """Edit task information"""
    task = db.session.get(Task, id) or abort(404)
    if task not in token_auth.current_user().assigneed_tasks:
        abort(403)
    task.update(data)
    db.session.commit()
    return task


@tasks.route('/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@response(empty_schema, 204)
@other_responses({403: 'Not allowed to delete', 404: 'Task not found'})
def delete(id):
    """Edit task information"""
    task = db.session.get(Task, id) or abort(404)
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
def get_all_assigned():
    """Retrieve tasks assigned to authenticated user."""
    return token_auth.current_user().assigned_tasks


@tasks.route('/assigned/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({404: 'Task or user not found',
    403: 'Not allowed to read'})
def get_assigned(id):
    """Read a assigned task"""
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task not in token_auth.current_user().assigned_tasks:
        abort(403)
    return task


@tasks.route('/assigned/<int:id>', methods=['POST'])
@authenticate(token_auth)
@response(empty_schema, 201)
@other_responses({404: 'Task or user not found',
    405: 'Assign to self not allowed', 409: 'Already assigned'})
def set_assigned(id):
    """Assign authenticated user to task"""
    task = db.session.get(Task, id)
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
@response(task_schema)
@other_responses({403: 'Not allowed to edit', 404: 'Task not found'})
def put_assigned(data, id):
    """Add input to task as assigned user"""
    task = db.session.get(Task, id) or abort(404)
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
def get_all_assigneed():
    """Retrieve tasks assigned from authenticated user."""
    return token_auth.current_user().assigneed_tasks


@tasks.route('/assigneed/<int:id>')
@authenticate(token_auth)
@response(task_schema)
@other_responses({404: 'Task not found', 403: 'Not allowed to read'})
def get_assigneed(id):
    """Read a assigneed task"""
    task = db.session.get(Task, id)
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
def put_assigneed(data, id):
    """Edit task as task creator"""
    task = db.session.get(Task, id) or abort(404)
    if task not in token_auth.current_user().assigneed_tasks:
        abort(403)
    task.update(data)
    db.session.commit()
    return task