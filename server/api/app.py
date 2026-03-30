from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from apifairy import APIFairy
from flask_caching import Cache
from celery import Celery, Task

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow() # Initialize AFTER flask-sqlalchemy
cors = CORS()
mail = Mail()
apifairy = APIFairy()
cache = Cache()

# From the Flask docs.
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config, namespace="CELERY")
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # models are registered with SQLAlchemy when they're imported. This is for SQLAlchemy to see them,
    # and for the migrations to be able to find the model definitions
    from api import models
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app, supports_credentials=True) # Need this for accepting cross-origin cookies. Injects the Access-Control-Allow-Credentials header in responses.
    mail.init_app(app)
    apifairy.init_app(app)
    cache.init_app(app)
    celery_init_app(app)

    # Error handlers for both Flask and apifairy (ADD: SQLAlchemy integrity errors)
    from api.errors import errors
    app.register_blueprint(errors)

    # Auth token creation, verification, and revocation
    from api.tokens import tokens
    app.register_blueprint(tokens, url_prefix="/api")

    # Core functionality
    from api.main import main
    app.register_blueprint(main, url_prefix="/api")

    # Admin functionality
    from api.admin import admin
    app.register_blueprint(admin, url_prefix="/api")

    # Company user functionality
    from api.company import company
    app.register_blueprint(company, url_prefix="/api")

    # Student user functionality
    from api.student import student
    app.register_blueprint(student, url_prefix="/api")

    # CLI functions (for inital DB setup)
    from api.cli import bp as cli_bp
    app.register_blueprint(cli_bp)

    # Shell context for easier DB manipulation via the CLI
    @app.shell_context_processor
    def make_shell_context():
        return {"db": db}

    return app