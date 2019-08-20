from flask import Blueprint

blueprint = Blueprint(
    'factory_blueprint',
    __name__,
    url_prefix='/AdminDashboard/factory',
    template_folder='templates',
    static_folder='static'
)
