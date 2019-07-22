from flask import request
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.api.model.user import User
from app.api.model.com import Company
from app.api.model.car import Car

com_app = Namespace('Company', description='All Company related endpoints')

auth_model = com_app.model('authentication and authorization', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

signup_model = com_app.model('Company sign up', {
    'company_name': fields.String(required=True, description='Factory Name'),
    # 'username': fields.String(required=True, description='Factory Name'),
    'address': fields.String(required=True, description='Factory address'),
    'email': fields.String(required=True, description='Factory Name'),
    # 'password': fields.String(required=True, description='Factory Name'),
    'phone': fields.String(required=True, description='delegate Phone number')

})

device_token_model = com_app.model('assign token to device', {
    'device_token': fields.String(required=True, description='device token')

})


def company_required(fun):
    def decorator(*args, **kwargs):
        user = User.query.get(current_user.id)
        if not user.isCompany:
            response_opj = {
                'status': 'failed',
                'message': 'you are not a company user!'
            }
            return response_opj, 401
        return fun(*args, **kwargs)

    return decorator


@com_app.route('/Login')
class Login(Resource):
    @com_app.expect(auth_model)
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.query.filter_by(email=email).first()
            if not (user and user.check_password(password) and user.isCompany):
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


@com_app.route('/Logout')
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
@com_app.route('/SignUp')
class SignUp(Resource):
    @com_app.expect(signup_model)
    def post(self):
        data = request.json
        try:
            company_name = data.get('company_name')
            username = company_name  #data.get('username')
            email = data.get('email')
            password = 'company' #data.get('password')
            address = data.get('address')
            phone = data.get('phone')

            role = 1
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
            user = User.query.filter_by(phone=phone).first()
            if user:
                response_opj = {
                    'status': 'failed',
                    'message': 'user with entered phone already exist!'
                }
                return response_opj, 409
            user = User(username=username, email=email, role=role, password=password, phone=phone)
            db.session.add(user)
            com = Company.query.filter_by(name=company_name).first()
            if com:
                response_opj = {
                    'status': 'failed',
                    'message': 'company with entered name already exist!'
                }
                return response_opj, 409
            com = Company.query.filter_by(address=address).first()
            if com:
                response_opj = {
                    'status': 'failed',
                    'message': 'company with entered address already exist!'
                }
                return response_opj, 409

            com = Company(name=company_name, account=user.id, address=address)
            db.session.add(com)
            db.session.commit()
            response_opj = {
                'status': 'success',
                'message': 'Successfully Signed up'
            }
            return response_opj, 201
        except Exception as e:
            print('Exception in company sign up:', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


# TODO if car is busy what if i want it's current order !
@com_app.route('/CompanyCarsList')
class CompanyCarsList(Resource):
    @login_required
    @company_required
    def get(self):
        try:
            company = Company.query.filter_by(_user_id=current_user.id).first()
            cars = Car.query.filter_by(_owner=company.id).all()
            print(cars)
            response_opj = {
                'status': 'success',
                'cars_list': [car.serialize() for car in cars]
            }
            return response_opj, 200

        except Exception as e:
            print('Exception in company cars list:', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500


@com_app.route('/RegisterDeviceToken')
@com_app.expect(device_token_model)
class RegisterDeviceToken(Resource):
    @login_required
    @company_required
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


@com_app.route('/CarLocation<id>')
class CarLocation(Resource):
    @login_required
    @company_required
    def get(self, id):
        try:
            car = Car.query.get(id)
            response_opj = {
                'status': 'success',
                'car_location_latitude': car.location_latitude,
                'car_location_longitude': car.location_longitude
            }
            return response_opj, 200

        except Exception as e:
            print('Exception in car location :', e)
            response_opj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_opj, 500
