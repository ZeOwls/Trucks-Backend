from flask import Blueprint

blueprint = Blueprint(
    'cars_blueprint_company',
    __name__,
    url_prefix='/CompanyDashboard/cars',
    template_folder='templates',
    static_folder='static'
)

