from flask import Blueprint

root = Blueprint(
    'root_blueprint',
    __name__,
    url_prefix='/',
    template_folder='templates',
    static_folder='static'
)
blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='/AdminDashboard',
    template_folder='templates',
    static_folder='static'
)

company_blueprint = Blueprint(
    'companyOrders_blueprint',
    __name__,
    url_prefix='/CompanyDashboard/OrdersList',
    template_folder='templates',
    static_folder='static'
)

factory_blueprint = Blueprint(
    'factoryOrders_blueprint',
    __name__,
    url_prefix='/FactoryDashboard/OrdersList',
    template_folder='templates',
    static_folder='static'
)
