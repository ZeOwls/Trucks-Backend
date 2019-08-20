from app.adminDashboard.driver import blueprint
from flask import render_template
from flask_login import login_required

from app.utils.login import admin_required

@blueprint.route('/')
@admin_required
def index():
    return render_template('driver_index.html')


@blueprint.route('/<template>')
@admin_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('error/<error>')
@admin_required
def route_error(error):
    print(error)
    return render_template("NewDriver" + '.html',error=error)
