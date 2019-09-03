from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from flask_googlemaps import GoogleMaps
import os
from redis import Redis
from rq import Queue
from flask_rq2 import RQ
from pyfcm import FCMNotification
import pandas as pd
from .config import config_by_name

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
cors = CORS()
rq = RQ()
notf_service = FCMNotification(
    api_key="AAAAWME4vPI:APA91bE6voNAtuajKkUKfuIc9_HYN2oW2x8g8guVdUa6tuG1_CtGzL5vdKQZphTk9axqfEuQMvi9_QdwgnEHA5IVhmphhThiO4Z4Yob6gTONR6APFeFdewWVtrR0q9LYVFoz3EIQXHiY")

# ************ Admin Dashboard blueprint **********
from app.api import blueprint as api_bl
from app.adminDashboard.base.routes import blueprint as base_admin
from app.adminDashboard.home.routes import blueprint as home_admin
from app.adminDashboard.factory.routes import blueprint as factory_admin
from app.adminDashboard.company.routes import blueprint as company_admin
from app.adminDashboard.driver.routes import blueprint as driver_admin
from app.adminDashboard.order.routes import blueprint as orders_admin

# ************* Company Dashboard blueprint *********
from app.adminDashboard.home.company_routs import com_blueprint as home_company
from app.adminDashboard.driver.company_routs import com_blueprint as drivers_company
from app.adminDashboard.car.routs import blueprint as cars_company
from app.adminDashboard.base.routes import company_blueprint as orders_company

# ************* Company Dashboard blueprint *********
from app.adminDashboard.home.factory_routs import factory_blueprint
from app.adminDashboard.base.routes import factory_blueprint as orders_factory
from app.adminDashboard.order.routes import factory_blueprint as new_order_factory

# *************** test ******************
from app.adminDashboard.base.routes import root


# TODO what to do with this and dashboard !!
# @login_manager.unauthorized_handler
# def unauthorized():
#     response_obj = {
#             'status': 'failed',
#             'message': 'unauthorized, please log in first'
#         }
#     return response_obj


def creat_app(config_name):
    app = Flask(__name__, static_folder='adminDashboard/base/static')
    app.config.from_object(config_by_name[config_name])
    app.config['GOOGLEMAPS_KEY'] = "AIzaSyBp1G6tb0v3JzSfcPtmKGwLI018Q-DL41E"
    GoogleMaps(app)
    db.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    rq.init_app(app)
    # register blueprints

    # test
    app.register_blueprint(root)

    # Admin Dashboard blueprints
    app.register_blueprint(api_bl)
    app.register_blueprint(base_admin)
    app.register_blueprint(home_admin)
    app.register_blueprint(factory_admin)
    app.register_blueprint(company_admin)
    app.register_blueprint(driver_admin)
    app.register_blueprint(orders_admin)

    # Company Dashboard blueprint
    app.register_blueprint(home_company)
    app.register_blueprint(cars_company)
    app.register_blueprint(drivers_company)
    app.register_blueprint(orders_company)

    # Factory Dashboard blueprint
    app.register_blueprint(factory_blueprint)
    app.register_blueprint(orders_factory)
    app.register_blueprint(new_order_factory)

    r = Redis(os.getenv('REDIS_URL', 'redis://localhost:6379'))

    return app, r


app, r = creat_app(os.getenv('TRANKAT') or 'dev')
q = Queue(connection=r)
