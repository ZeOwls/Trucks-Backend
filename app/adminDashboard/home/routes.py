import datetime
import time
from datetime import timedelta
import dateutil.relativedelta as dr
from flask_googlemaps import Map
from sqlalchemy import func

from app.adminDashboard.home import blueprint
from flask import render_template

from app.api.model.car import Car
from app.api.model.factory import Factory
from app.api.model.order import Order
from app.api.model.com import Company
from app.api.model.driver import Driver
from app.utils.login import admin_required


@blueprint.route('/Home')
@admin_required
def index():
    cars = Car.query.all()
    locations = [
        {
            'latitude': car.location_latitude,
            'longitude': car.location_longitude
        }
        for car in cars]  # long list of coordinates
    lat = 30.049232
    lng = 31.232027
    if len(locations):
        lat = locations[0]['latitude']
        lng = locations[0]['longitude']
    map = Map(
        lat=lat,
        lng=lng,
        identifier="view-side",
        zoom=10,
        style="height:500px;width:100%;margin:0;",
        markers=[(loc['latitude'], loc['longitude']) for loc in locations if loc['latitude'] and loc['longitude']],
        fit_markers_to_bounds=True
    )

    data = {}
    factory_num = Factory.query.filter(Factory.delegate_opj.has(account_status=1)).count()
    companies_num = Company.query.filter(Company.user_object.has(account_status=1)).count()
    drivers_num = Driver.query.filter_by(driver_status=1).count()
    status0 = Order.query.filter_by(status=0).count()
    status1 = Order.query.filter_by(status=1).count()
    status2 = Order.query.filter_by(status=2).count()
    status3 = Order.query.filter_by(status=3).count()
    status4 = Order.query.filter_by(status=4).count()
    status5 = Order.query.filter_by(status=5).count()
    daily = []
    monthly = []
    # get num of orders per day in last week
    day = 0
    month = 0
    while day < 7:
        number_of_orders = Order.query.filter(
            func.date(Order.ordered_at) == datetime.date.today() - timedelta(days=day)).count()
        daily.append(number_of_orders)
        day += 1

    while month < 12:
        m = (datetime.date.today() - dr.relativedelta(months=month)).month
        number_of_orders = Order.query.filter(
            func.extract('month', Order.ordered_at) == m).count()
        monthly.append(number_of_orders)
        month += 1
    data['factory_num'] = factory_num
    data['companies_num'] = companies_num
    data['drivers_num'] = drivers_num
    data['status0'] = status0
    data['status1'] = status1
    data['status2'] = status2
    data['status3'] = status3
    data['status4'] = status4
    data['status5'] = status5
    data['orders_daily'] = daily
    data['orders_monthly'] = monthly

    return render_template('admin_index.html', data=data, map=map)


@blueprint.route('/<template>')
@admin_required
def route_template(template):
    return render_template(template + '.html')
