import os
from app import create_app, db, cli
from app.models import User, Role, Permission, Follow, Post, Comment, Notification

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    if app.
    return dict(db=db, User=User, Role=Role, Permission=Permission,\
        Follow=Follow, Post=Post, Comment=Comment, Notification=Notification)