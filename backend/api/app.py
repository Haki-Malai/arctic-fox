from config import config
from flask import Flask, redirect, url_for
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from apifairy import APIFairy

mail = Mail()
db = SQLAlchemy()
apifairy = APIFairy()
ma = Marshmallow()

def create_app(config_name):
    app = Flask(__name__)
    from api.cli import run_script
    app.register_blueprint(run_script)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    apifairy.init_app(app)
    ma.init_app(app)

    # Import blueprints
    from api.errors import errors
    app.register_blueprint(errors)
    from api.tokens import tokens
    app.register_blueprint(tokens, url_prefix='/api/tokens')
    from api.users import users
    app.register_blueprint(users, url_prefix='/api/users')
    from api.posts import posts
    app.register_blueprint(posts, url_prefix='/api/posts')
    from api.comments import comments
    app.register_blueprint(comments, url_prefix='/api/comments')
    from api.notifications import notifications
    app.register_blueprint(notifications, url_prefix='/api/notification')
    from api.tasks import tasks
    app.register_blueprint(tasks, url_prefix='/api/tasks')

    @app.route('/')
    def index():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    return app