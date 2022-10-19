import os
from api import create_app, db, cli
from api.models import User, follower, Post, Comment, \
    Notification, Task, assigns

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))


# Define shell context
@app.shell_context_processor
def make_shell_context():
    #if app.config['DEBUG']:
        #db.drop_all()
        #db.create_all()
        #from api.fake import fake_admins, fake_users, fake_posts,\
            #fake_comments, fake_follows, fake_notifications, fake_tasks
        #fake_admins()
        #fake_users()
        #fake_posts()
        #fake_comments()
        #fake_tasks()
    return dict(db=db, User=User, follower=follower, Post=Post, Comment=Comment,
        Notification=Notification, Task=Task, Notificatin=Notification,
        u=User.query.first())