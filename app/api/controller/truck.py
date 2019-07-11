# from flask_login import login_required , current_user
# from flask import request
# from flask_restplus import Namespace, Resource, fields
#
# from app import db , login_manager
# from app.api.model.user import User
#
# #TODO how will login, how will know which car is it know!
#
# truck_app = Namespace('Truck', description='All Truck related endpoints')
# check_in = truck_app.model('check in', {
#     'truck_location_latitude': fields.Float(required=True, description='truck location latitude'),
#     'truck_location_longitude': fields.Float(required=True, description='truck location longitude')
# })
#
#
#
# @truck_app.route('/CheckIn')
# @login_required
# class CheckIn:
