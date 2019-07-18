from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
import os

from .config import config_by_name

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
cors = CORS()

from app.api import blueprint as api_bl
# from app.adminDashboard.base.routes import blueprint as base_admin
# from app.adminDashboard.home.routes import blueprint as home_admin

@login_manager.unauthorized_handler
def unauthorized():
    response_opj = {
            'status': 'failed',
            'message': 'unauthorized, please log in first'
        }
    return response_opj

def creat_app(config_name):
    app = Flask(__name__,static_folder='adminDashboard/base/static')
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    # register blueprints
    app.register_blueprint(api_bl)
    # app.register_blueprint(base_admin)
    # app.register_blueprint(home_admin)
    return app


app = creat_app(os.getenv('TRANKAT') or 'dev')
