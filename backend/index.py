import os
from api import create_app, db, cli
from api.models import User, Role, Permission, Follow, Post, Comment, Notification

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
cli.register(app)


# Define shell context
@app.shell_context_processor
def make_shell_context():
    if app.config['DEBUG']:
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        from api.fake import fake_users, fake_posts, fake_comments
        fake_users()
        fake_posts()
        fake_comments()
    return dict(db=db, User=User, Role=Role, Permission=Permission,\
        Follow=Follow, Post=Post, Comment=Comment, Notification=Notification)