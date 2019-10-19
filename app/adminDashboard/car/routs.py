from flask import render_template
from flask_login import current_user

from app.api.model.car import Car
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


@blueprint.route("/EditCar<car_id>")
def edit_car(car_id):
    car = Car.query.get(car_id)
    plate_number = car.number
    type = car._type
    capacity = car.capacity
    color = car.color
    maktura_plate_number = car.maktura_plate_number
    data = {
        "car_id": car.id,
        "plate_number": plate_number,
        "type": type,
        "capacity": capacity,
        "color": color,
        "maktura_plate_number": maktura_plate_number
    }
    return render_template("edit_car.html", data=data)




@blueprint.route('error/<error>')
@company_required
def route_error(error):
    print(error)
    return render_template("NewCar" + '.html', error=error)
