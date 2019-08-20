import datetime
import time
from datetime import timedelta
import dateutil.relativedelta as dr
from sqlalchemy import func

from app.adminDashboard.factory import blueprint
from flask import render_template
from flask_login import login_required
from app.api.model.factory import Factory
from app.api.model.order import Order
from app.api.model.com import Company
from app.api.model.driver import Driver
from app.utils.login import admin_required


@blueprint.route('/')
@admin_required
def index():
    return render_template('factory_index.html')


@blueprint.route('/<template>')
@admin_required
def route_template(template):
    return render_template(template + '.html')

@blueprint.route('error/<error>')
@admin_required
def route_error(error):
    print(error)
    return render_template("NewFactory" + '.html',error=error)
