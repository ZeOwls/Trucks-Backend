from flask import request
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required, login_user, logout_user, current_user

from app.api.model.user import User
from app import db
from app.api.model.factory import Factory
from app.api.model.order import Order, OrderCarsTypes
from app.api.model.car import available_type

fac_app = Namespace('Factory', description='All Factory related endpoints')
auth_model = fac_app.model('authentication and authorization', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

signup_model = fac_app.model('Factory sign up', {
    'factory_name': fields.String(required=True, description='Factory Name'),
    'username': fields.String(required=True, description='Factory Name'),
    'address': fields.String(required=True, description='Factory address'),
    'email': fields.String(required=True, description='Factory Name'),
    'password': fields.String(required=True, description='Factory Name'),
    'factory_hotline': fields.String(required=True, description='Factory Hotline'),
    'delegate_phone': fields.String(required=True, description='delegate Phone number'),

})

profile_model = fac_app.model('Factory profile', {
    'factory_name': fields.String(required=True, description='Factory Name'),
    'delegate_name': fields.String(required=True, description='delegate Name'),
    'delegate_phone': fields.String(required=True, description='delegate Phone number'),
    'factory_address': fields.String(required=True, description='Factory address'),
    'factory_email': fields.String(required=True, description='Factory E-mail'),
    'factory_hotline': fields.String(required=True, description='Factory Hotline')

})

order_model = fac_app.model('create new order', {
    'from_latitude': fields.Float(required=True, description='latitude of Receiving location'),
    'from_longitude': fields.Float(required=True, description='longitude of Receiving location'),
    'to_latitude': fields.Float(required=True, description='latitude of Delivery location'),
    'to_longitude': fields.Float(required=True, description='longitude of Delivery location'),
    'pickup_location': fields.String(required=True, description='Order pickup location location'),
    'dropoff_location': fields.String(required=True, description='Order drop off location'),
    'trilla': fields.Integer(required=True, description='Number of Trilla wanted '),
    'maktura': fields.Integer(required=True, description='Number of maktura wanted')
})

device_token_model = fac_app.model('assign token to device', {
    'device_token': fields.String(required=True, description='device token')

})


# TODO make sure account is factory account!

@fac_app.route('/Login')
class Login(Resource):
    @fac_app.expect(auth_model)
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.query.filter_by(email=email).first()
            if not (user and user.check_password(password) and user.isFactory):
                response_opj = {
                    'status': 'failed',
                    'message': 'Email or password is wrong'
                }
                return response_opj, 401

            response_opj = {
                'status': 'success',
                'message': 'Successfully logged in'

            }
            login_user(user)
            return response_opj, 200

        except Exception as e:
            print("exception at login:", e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


@fac_app.route('/Logout')
class Logout(Resource):
    @login_required
    def get(self):
        try:
            logout_user()
            response_opj = {
                "status": "success",
                "message": "Successfully logged out"
            }
            return response_opj, 200
        except Exception as e:
            print("Exception at logout:", str(e))
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


# TODO Admin only ?? ask arafa ?
@fac_app.route('/SignUp')
class SignUp(Resource):
    @fac_app.expect(signup_model)
    def post(self):
        data = request.json
        try:
            factory_name = data.get('factory_name')
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            address = data.get('address')
            factory_hotline = data.get('factory_hotline')
            delegate_phone = data.get('delegate_phone')

            role = 2
            user = User.query.filter_by(email=email).first()
            if user:
                response_opj = {
                    'status': 'failed',
                    'message': 'user with entered E-mail already exist!'
                }
                return response_opj, 409
            user = User.query.filter_by(username=username).first()
            if user:
                response_opj = {
                    'status': 'failed',
                    'message': 'user with entered name already exist!'
                }
                return response_opj, 409
            user = User.query.filter_by(phone=delegate_phone).first()
            if user:
                response_opj = {
                    'status': 'failed',
                    'message': 'user with entered phone already exist!'
                }
                return response_opj, 409
            user = User(username=username, email=email, role=role, password=password, phone=delegate_phone)
            db.session.add(user)
            fac = Factory.query.filter_by(name=factory_name).first()
            if fac:
                response_opj = {
                    'status': 'failed',
                    'message': 'factory with entered name already exist!'
                }
                return response_opj, 409
            fac = Factory.query.filter_by(address=address).first()
            if fac:
                response_opj = {
                    'status': 'failed',
                    'message': 'factory with entered address already exist!'
                }
                return response_opj, 409
            fac = Factory.query.filter_by(hotline=factory_hotline).first()
            if fac:
                response_opj = {
                    'status': 'failed',
                    'message': 'factory with entered hot line already exist!'
                }
                return response_opj, 409
            fac = Factory(name=factory_name, delegate=user.id, address=address, hotline=factory_hotline)
            db.session.add(fac)
            db.session.commit()
            response_opj = {
                'status': 'success',
                'message': 'Successfully Signed up'
            }
            return response_opj, 201
        except Exception as e:
            print('Exception in factory sign up:', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


@fac_app.route('/FactoryOrdersList')
class OrderList(Resource):
    @login_required
    def get(self):
        try:
            orders = Order.query.filter_by(factory_id=current_user.id).all()
            orders_opj = [order.small_serialize() for order in orders]
            response_opj = {
                'status': 'success',
                'orders-Info': orders_opj
            }
            return response_opj, 200
        except Exception as e:
            print(e)
            return 500


@fac_app.route('/OrderDetails<id>')
class OrderDetails(Resource):
    @login_required
    def get(self, id):
        try:
            order = Order.query.get(id)
            if order.factory_id != current_user.id:
                response_opj = {
                    'status': 'failed',
                    'message': "You can't access this order!"
                }
                return response_opj, 401

            if not order:
                response_opj = {
                    'status': 'failed',
                    'message': 'Wrong order ID!'
                }
                return response_opj, 422

            order_opj = order.serialize()
            response_opj = {
                'status': 'success',
                'order-Info': order_opj
            }
            return response_opj, 200
        except Exception as e:
            print(e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


@fac_app.route('/NewOrder')
class NewOrder(Resource):
    @login_required
    @fac_app.expect(order_model)
    def post(self):
        data = request.json
        try:
            from_latitude = data.get('from_latitude')  # دوائر العرض
            from_longitude = data.get('from_longitude')  # خطوط الطول
            to_latitude = data.get('to_latitude')  # دوائر العرض
            to_longitude = data.get('to_longitude')  # خطوط الطول
            pickup_location = data.get('pickup_location')
            dropoff_location = data.get('dropoff_location')
            factory_id = current_user.id
            num_of_trilla = data.get('trilla')
            num_of_maktura = data.get('maktura')
            num_of_cars = num_of_maktura + num_of_trilla
            order = Order(from_latitude=from_latitude, from_longitude=from_longitude, to_latitude=to_latitude,
                          to_longitude=to_longitude, pickup_location=pickup_location, dropoff_location=dropoff_location,
                          factory_id=factory_id, num_of_cars=num_of_cars)
            db.session.add(order)
            db.session.commit()
            print(order)
            for car_type in available_type:
                car = OrderCarsTypes(order_id=order.id, cars_num=data.get(car_type) or 0, car_type=car_type)
                db.session.add(car)

            db.session.commit()
            response_opj = {
                'status': 'success',
                'message': 'Successfully crate new order'
            }
            return response_opj, 201
        except Exception as e:
            print("Exception in new order:", e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


@fac_app.route('/RegisterDeviceToken')
class RegisterDeviceToken(Resource):
    @login_required
    @fac_app.expect(device_token_model)
    def post(self):
        data = request.json
        try:
            user = User.query.get(current_user.id)
            token = data.get('device_token')
            user.device_token = token
            db.session.commit()
            response_opj = {
                'status': 'success',
                'message': 'Successfully add Device token'
            }
            return response_opj, 201

        except Exception as e:
            print('exception in add device token:', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


@fac_app.route('/FactoryProfile')
class FactoryProfile(Resource):
    @login_required
    def get(self):
        try:
            user = User.query.get(current_user.id)
            delegate_name = user.username
            delegate_phone = user.phone
            factory_email = user.email
            factory = Factory.query.filter_by(_delegate_id=user.id).first()
            factory_name = factory.name
            factory_address = factory.address
            response_opj = {
                'status': 'success',
                'factory_code': factory.id,
                'delegate_name': delegate_name,
                'delegate_phone': delegate_phone,
                'factory_name': factory_name,
                'factory_email': factory_email,
                'factory_address': factory_address,
                'factory_image': factory_name + '.png',
                'factory_hotline': factory.hotline
            }
            return response_opj, 200

        except Exception as e:
            print('Exception in get profile Info', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500

    @fac_app.expect(profile_model)
    def put(self):
        data = request.json
        try:
            delegate_name = data.get('delegate_name')
            delegate_phone = data.get('delegate_phone')
            factory_email = data.get('factory_email')
            factory_name = data.get('factory_name')
            factory_address = data.get('factory_address')
            factory_hotline = data.get('factory_hotline')
            user = User.query.get(current_user.id)
            user.username = delegate_name
            user.phone = delegate_phone
            user.email = factory_email
            factory = Factory.query.filter_by(_delegate_id=user.id).first()
            factory.factory_name = factory_name
            factory.factory_address = factory_address
            factory.hotline = factory_hotline
            db.session.commit()
            response_opj = {
                'status': 'success',
                'delegate_name': delegate_name,
                'delegate_phone': delegate_phone,
                'factory_name': factory_name,
                'factory_email': factory_email,
                'factory_address': factory_address,
                'factory_hotline': factory_hotline
            }
            return response_opj, 200

        except Exception as e:
            print('Exception in put profile Info', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500
