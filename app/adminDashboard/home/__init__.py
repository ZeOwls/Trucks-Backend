from flask import Blueprint

blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix='/AdminDashboard/home',
    template_folder='templates',
    static_folder='static'
)

com_blueprint = Blueprint(
    'home_blueprint_company',
    __name__,
    url_prefix='/CompanyDashboard/home',
    template_folder='templates',
    static_folder='static'
)

factory_blueprint = Blueprint(
    'home_blueprint_factory',
    __name__,
    url_prefix='/FactoryDashboard/home',
    template_folder='templates',
    static_folder='static'
)