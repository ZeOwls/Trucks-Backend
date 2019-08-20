from flask import Blueprint

blueprint = Blueprint(
    'driver_blueprint',
    __name__,
    url_prefix='/AdminDashboard/driver',
    template_folder='templates',
    static_folder='static'
)

com_blueprint = Blueprint(
    'driver_blueprint_company',
    __name__,
    url_prefix='/CompanyDashboard/drivers',
    template_folder='templates',
    static_folder='static'
)