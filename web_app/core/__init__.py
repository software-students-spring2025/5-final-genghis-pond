from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from .config import Config

# Initialize various modules
mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    # Blueprints
    from core.routes.main import main
    from core.routes.auth import auth
    from core.routes.sightings import sightings
    from core.routes.user import user

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(sightings)
    app.register_blueprint(user)
    return app


# idk why having these lines are necessary but
# everything breaks if they aren't here
mongo = mongo
login_manager = login_manager
bcrypt = bcrypt
