from app.adminDashboard.driver import blueprint
from flask import render_template
from flask_login import login_required

from app.api.model.driver import Driver
from app.utils.login import admin_required


@blueprint.route('/')
@admin_required
def index():
    return render_template('driver_index.html')


@blueprint.route('/<template>')
@admin_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route("/EditDriver/<driver_id>")
@login_required
def edit_driver(driver_id):
    driver = Driver.query.get(driver_id)
    driver_name = driver.name
    driver_license_type = driver.license_type
    driver_license_number = driver.license_number
    driver_phone = driver.phone
    data = {
        "driver_id": driver_id,
        "name": driver_name,
        "license_type": driver_license_type,
        "license_number": driver_license_number,
        "phone": driver_phone
    }
    return render_template("edit_driver.html", data=data)


@blueprint.route('error/<error>')
@admin_required
def route_error(error):
    print(error)
    return render_template("NewDriver" + '.html', error=error)
