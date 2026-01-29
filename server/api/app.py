from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from apifairy import APIFairy

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow() # Initialize AFTER flask-sqlalchemy
cors = CORS()
mail = Mail()
apifairy = APIFairy()

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

    # Error handlers for both Flask and apifairy (ADD: SQLAlchemy integrity errors)
    # from api.errors import errors
    # app.register_blueprint(errors)

    # Auth token creation, verification, and revocation
    # from api.tokens import tokens
    # app.register_blueprint(tokens, url_prefix="/api")

    # Core functionality
    from api.main import main
    app.register_blueprint(main, url_prefix="/api")

    # CLI functions (for inital DB setup and seeding tables with Faker)
    # from api.cli import bp as cli_bp
    # app.register_blueprint(cli_bp)

    return app