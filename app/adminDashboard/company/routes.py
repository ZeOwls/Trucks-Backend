from app.adminDashboard.company import blueprint
from flask import render_template
from flask_login import login_required



@blueprint.route('/')
@login_required
def index():
    return render_template('company_index.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('error/<error>')
@login_required
def route_error(error):
    return render_template("NewCompany" + '.html', error=error)
