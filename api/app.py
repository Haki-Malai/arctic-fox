from flask import Flask, redirect, url_for, request
from alchemical.flask import Alchemical
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from apifairy import APIFairy
from celery import Celery
import redis
import logging

from config import Config
from utils.aws_wrapper import AWSWrapper

from typing import Type, Dict, Any

db = Alchemical()
migrate = Migrate()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()
cache = Cache()
aws_wrapper = AWSWrapper()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
rd = redis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)


def create_app(config_class: Type[Config] = Config) -> Flask:
    """Create and configure an instance of the Flask application.

    :param config_class: The configuration class to use.

    :return: The Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.sort_keys = False

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})
    mail.init_app(app)
    apifairy.init_app(app)
    cache.init_app(app)
    aws_wrapper.init_app(app)
    celery.conf.update(app.config)

    # Blueprints routes
    from api.routes.health import bp as health_bp
    app.register_blueprint(health_bp)
    from api.routes.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from api.routes.tokens import bp as tokens_bp
    app.register_blueprint(tokens_bp, url_prefix='/api/v1')
    from api.routes.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api/v1')
    from api.routes.folders import bp as folders_bp
    app.register_blueprint(folders_bp, url_prefix='/api/v1')
    from api.routes.files import bp as files_bp
    app.register_blueprint(files_bp, url_prefix='/api/v1')

    # CLI commands
    from cli.fake import fake
    app.register_blueprint(fake)
    from cli.drop import bp as drop_bp
    app.register_blueprint(drop_bp)
    from cli.create import bp as create_bp
    app.register_blueprint(create_bp)

    @apifairy.process_apispec
    def apispec_processor(spec:dict) -> dict:
        """Processes the API specification.

        :param spec: The API specification.
        :returns: The processed API specification.
        """
        spec['servers'] = [
            {
                'url': f'https://{request.host}',
                'description': 'HTTPS Server'
            },
            {
                'url': f'http://{request.host}',
                'description': 'HTTP Server'
            }
        ]
        return spec

    @app.shell_context_processor
    def shell_context() -> Dict[str, Any]:
        """Defines the shell context.

        :returns: The shell context.
        """
        import api.models as models

        ctx = {'db': db}
        for attr in dir(models):
            model = getattr(models, attr)
            if hasattr(model, '__bases__') and \
                    db.Model in getattr(model, '__bases__'):
                ctx[attr] = model
        return ctx

    @app.route('/')
    @app.route('/api')
    @app.route('/api/v1')
    def index() -> str:
        """Redirects to the API documentation.

        :returns: The redirect response.
        """
        return redirect(url_for('apifairy.docs'))

    if not app.debug:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    return app
