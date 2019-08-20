from flask import Blueprint

blueprint = Blueprint(
    'orders_blueprint',
    __name__,
    url_prefix='/AdminDashboard/orders',
    template_folder='templates',
    static_folder='static'
)

factory_blueprint = Blueprint(
    'factory_newOrder_blueprint',
    __name__,
    url_prefix='/FactoryDashboard/NewOrder',
    template_folder='templates',
    static_folder='static'
)