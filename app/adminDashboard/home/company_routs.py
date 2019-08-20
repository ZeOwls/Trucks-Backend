from flask import render_template
from flask_login import current_user

from app.api.model.car import Car
from app.api.model.com import Company
from app.api.model.driver import Driver
from app.api.model.order import Order
from app.api.model.order_driver_car import OrderCarsAndDrivers
from . import com_blueprint

from app.utils.login import company_required


@com_blueprint.route('/')
@company_required
def company_index():
    data = {}
    company_id = Company.query.filter_by(_user_id=current_user.id).first().id
    orders_num = OrderCarsAndDrivers.query.filter_by(company_id=company_id).group_by(
        OrderCarsAndDrivers.order_id).count()
    drivers = Driver.query.filter(Driver.company_id == company_id, Driver.driver_status == 1).all()
    drivers_num = len(drivers)
    drivers = [driver.serialize() for driver in drivers[0:min(drivers_num, 5)]]
    cars = Car.query.filter_by(_owner=company_id).filter(Car.user_obj.has(account_status=1))
    free_cars_num = cars.filter_by(_status=0).count()
    busy_cars_num = cars.filter_by(_status=1).count()
    cars_num = cars.count()
    cars_preview = [car.serialize() for car in cars.all()[0:min(cars_num, 5)]]
    data["orders_num"] = orders_num
    data["drivers_num"] = drivers_num
    data["cars_num"] = cars_num
    data["cars_preview"] = cars_preview
    data["drivers_preview"] = drivers
    data["busy_cars_num"] = busy_cars_num
    data["free_cars_num"] = free_cars_num
    return render_template('company_home.html', data=data), 200
