from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os


basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

login_manager = LoginManager()
#login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'main.login'
login_manager.login_message = u"Please log in first."


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hard to guess string'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    #app.config.from_object(config[config_name])
    #config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # Attach routes
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
