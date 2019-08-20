from flask import render_template
from flask_login import current_user

from app.api.model.factory import Factory
from app.api.model.order import Order
from . import factory_blueprint
from app.utils.login import factory_required


@factory_blueprint.route('/')
@factory_required
def factory_index():
    data = {}
    factory_id = Factory.query.filter_by(_delegate_id=current_user.id).first().id
    orders = Order.query.filter_by(factory_id=factory_id)
    status0 = orders.filter_by(status=0).count()
    status1 = orders.filter_by(status=1).count()
    status2 = orders.filter_by(status=2).count()
    status3 = orders.filter_by(status=3).count()
    status4 = orders.filter_by(status=4).count()
    status5 = orders.filter_by(status=5).count()
    data['status0'] = status0
    data['status1'] = status1
    data['status2'] = status2
    data['status3'] = status3
    data['status4'] = status4
    data['status5'] = status5
    orders = orders.all()
    orders = [order.serialize() for order in orders[0:min(5,len(orders))]]
    print(orders)
    data['orders_preview'] = orders
    return render_template('factory_home.html', data=data)
