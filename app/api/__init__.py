from flask import Blueprint
from flask_restplus import Api

from .controller.factory import fac_app as factory
from .controller.com import com_app as company
blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title="Api for Trankat",
          version='1.0',
          doc='/'
          )


# add name spaces
api.add_namespace(factory,'/factory')
api.add_namespace(company,'/company')