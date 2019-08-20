from app.adminDashboard.order import blueprint, factory_blueprint
from flask import render_template

from app.utils.login import admin_required, factory_required


@blueprint.route('/')
@admin_required
def index():
    return render_template('order_index.html')


@blueprint.route('/<template>')
@admin_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('error/<error>')
@admin_required
def route_error(error):
    return render_template("NewOrder" + '.html', error=error)


@factory_blueprint.route('/')
@factory_required
def NewOrder():
    return render_template("NewOrder.html"), 200


@factory_blueprint.route('/error<error>')
@factory_required
def factory_route_error(error):
    return render_template("NewOrder" + '.html', error=error)