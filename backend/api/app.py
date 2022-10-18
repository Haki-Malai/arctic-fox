from flask import Flask, redirect, url_for
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from apifairy import APIFairy
from config import config

mail = Mail()
db = SQLAlchemy()
apifairy = APIFairy()
ma = Marshmallow()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    apifairy.init_app(app)
    ma.init_app(app)

    # Import blueprints
    from api.errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)
    from api.tokens import tokens as tokens_blueprint
    app.register_blueprint(tokens_blueprint, url_prefix='/api/tokens')
    from api.users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/api/users')
    from api.posts import posts as posts_blueprint
    app.register_blueprint(posts_blueprint, url_prefix='/api/posts')

    @app.route('/')
    def index():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    return app