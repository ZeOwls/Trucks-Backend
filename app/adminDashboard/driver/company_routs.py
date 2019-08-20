from flask import render_template

from . import com_blueprint

from app.utils.login import company_required

@com_blueprint.route('/')
@company_required
def index():
    return render_template('company_drivers.html')

@com_blueprint.route('/<template>')
@company_required
def route_template(template):
    return render_template(template + '.html')

@com_blueprint.route('error/<error>')
@company_required
def route_error(error):
    print(error)
    return render_template("NewDriver" + '.html',error=error)