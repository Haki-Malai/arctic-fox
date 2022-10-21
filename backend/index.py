import os
from api import create_app, db, cli
from api.models import User, follower, Post, Comment, \
    Notification, Task, assignment

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))


# Define shell context
@app.shell_context_processor
def make_shell_context():
    db.create_all()
    return dict(db=db, User=User, follower=follower, Post=Post, Comment=Comment,
        Notification=Notification, Task=Task, Notificatin=Notification,
        assignment=assignment, u=User.query.first())