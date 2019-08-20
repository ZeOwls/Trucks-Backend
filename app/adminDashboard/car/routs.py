from flask import render_template
from flask_login import current_user

from app.api.model.com import Company
from app.utils.login import company_required
from . import blueprint


@blueprint.route('/')
@company_required
def company_cars():
    return render_template('company_cars.html'), 200


@blueprint.route('/<template>')
@company_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('error/<error>')
@company_required
def route_error(error):
    print(error)
    return render_template("NewCar" + '.html', error=error)
