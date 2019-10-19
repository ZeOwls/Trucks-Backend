import os
# from firebase_admin import messaging

from flask import request, redirect, url_for
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required, login_user, logout_user, current_user
from functools import wraps

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import db, notf_service
from app.api.model.driver import Driver
from app.utils.login import company_required
from app.utils.background_jobs import export_cars, import_cars
from app.api.model.order import Order
from app.api.model.order_driver_car import OrderCarsAndDrivers
from app.api.model.user import User
from app.api.model.com import Company
from app.api.model.car import Car
from app.utils.upload_images import upload_file_to_s3

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


@com_app.route('/Login')
class Login(Resource):
    @com_app.expect(auth_model)
    def post(self):
        print("we are here")
        data = request.json
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.query.filter_by(email=email).first()
            if not (user and user.check_password(password) and user.isCompany and user.account_status != -1):
                response_obj = {
                    'status': 'failed',
                    'message': 'Email or password is wrong'
                }
                return response_obj, 401
            if user.account_status == 0:
                response_obj = {
                    'status': 'failed',
                    'message': "Admin didn't approve this account yet!"
                }
                return response_obj, 401
            response_obj = {
                'status': 'success',
                'message': 'Successfully logged in'

            }
            login_user(user)
            return response_obj, 200

        except Exception as e:
            print("exception at login:", e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/Logout')
class Logout(Resource):
    @company_required
    def get(self):
        try:
            logout_user()
            response_obj = {
                "status": "success",
                "message": "Successfully logged out"
            }
            return response_obj, 200
        except Exception as e:
            print("Exception at logout:", str(e))
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/SignUp')
class SignUp(Resource):
    @com_app.expect(signup_model)
    def post(self):
        data = request.json
        print(data)
        try:
            company_name = data.get('company_name')
            username = company_name  # data.get('username')
            email = data.get('email')
            # TODO generate password, and send mail
            password = User.generate_pass()  # 'company'  # data.get('password')
            address = data.get('address')
            phone = data.get('phone')
            # img = request.files['company_logo']
            role = 1
            user = User.query.filter_by(email=email).first()
            if user:
                response_obj = {
                    'status': 'failed',
                    'message': 'user with entered E-mail already exist!'
                }
                return response_obj, 409
            user = User.query.filter_by(username=username).first()
            if user:
                response_obj = {
                    'status': 'failed',
                    'message': 'user with entered name already exist!'
                }
                return response_obj, 409
            user = User.query.filter_by(phone=phone).first()
            if user:
                response_obj = {
                    'status': 'failed',
                    'message': 'user with entered phone already exist!'
                }
                return response_obj, 409
            user = User(username=username, email=email, role=role, password=password, phone=phone)
            db.session.add(user)
            com = Company.query.filter_by(name=company_name).first()
            if com:
                response_obj = {
                    'status': 'failed',
                    'message': 'company with entered name already exist!'
                }
                return response_obj, 409
            com = Company.query.filter_by(address=address).first()
            if com:
                response_obj = {
                    'status': 'failed',
                    'message': 'company with entered address already exist!'
                }
                return response_obj, 409

            # _, file_extension = os.path.splitext(img.filename)
            # url = upload_file_to_s3(img, file_name=company_name + file_extension, folder='company_logo')
            # com = Company(name=company_name, account=user.id, address=address, logo=url)
            com = Company(name=company_name, account=user.id, address=address)
            db.session.add(com)
            db.session.commit()
            admin_users = User.query.filter_by(role=3).all()
            for admin in admin_users:
                if admin.device_token:
                    device_token = admin.device_token
                    message_title = "New Company"
                    message_body = "There are new Company!"
                    click_action = "/AdminDashboard/company"
                    result = notf_service.notify_single_device(registration_id=device_token,
                                                               message_title=message_title,
                                                               click_action=click_action, message_body=message_body)
            response_obj = {
                'status': 'success',
                'message': 'Successfully Signed up'
            }
            return response_obj, 201
        except Exception as e:
            print('Exception in company sign up:', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/NewCompany')
class NewCompany(Resource):
    def post(self):
        data = request.form
        company_name = data.get('company_name')
        username = company_name  # data.get('username')
        email = data.get('email')
        password = User.generate_pass()
        address = data.get('address')
        phone = data.get('company_phone')
        role = 1
        user = User.query.filter_by(email=email).first()
        # img = request.files['company_logo']
        if user:
            return redirect(
                url_for('base_blueprint.SignupCompany', error="FAILED: user with entered E-mail already exist!"))

        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(
                url_for('base_blueprint.SignupCompany', error="FAILED: user with entered name already exist!"))

        user = User.query.filter_by(phone=phone).first()
        if user:
            return redirect(
                url_for('base_blueprint.SignupCompany', error="FAILED: user with entered phone already exist!"))

        user = User(username=username, email=email, role=role, password=password, phone=phone)
        db.session.add(user)
        com = Company.query.filter_by(name=company_name).first()
        if com:
            return redirect(
                url_for('base_blueprint.SignupCompany', error="FAILED: company with entered name already exist!"))

        com = Company.query.filter_by(address=address).first()
        if com:
            return redirect(
                url_for('base_blueprint.SignupCompany', error="FAILED: company with entered address already exist!"))
        # _, file_extension = os.path.splitext(img.filename)
        # url = upload_file_to_s3(img, file_name=company_name + file_extension, folder='company_logo')
        com = Company(name=company_name, account=user.id, address=address)
        db.session.add(com)
        db.session.commit()
        message_title = "New Company"
        message_body = "There are New company signed up, check pending companies!"
        device_token = "fQQZG641vkY:APA91bH02cIkdvFru7j7n6zwZzitFqZLvrT-IPW6RLuQRJfdSjHRNzG-0HWxd3aL6FsBQMFmTl3X00GaB8NkcTyjQXTmBoaSk2KQJ2Qm2JYvaDdUXzOTomEPhoY_jzFcVILwDtMlUaSR"
        result = notf_service.notify_single_device(registration_id=device_token, message_title=message_title,
                                                   message_body=message_body, click_action="/AdminDashboard/company")
        admin_users = User.query.filter_by(role=3).all()
        for admin in admin_users:
            if admin.device_token:
                device_token = admin.device_token
                message_title = "New Company"
                message_body = "There are new Company!"
                click_action = "/AdminDashboard/company"
                result = notf_service.notify_single_device(registration_id=device_token,
                                                           message_title=message_title,
                                                           click_action=click_action, message_body=message_body)
        return redirect(url_for('base_blueprint.login',
                                message="Successfully Signed up, waiting for Admin approve then you will "
                                        "receive Accepted E-mail from us"))


@com_app.route('/CompanyCarsList')
class CompanyCarsList(Resource):
    @company_required
    def get(self):
        try:
            company = Company.query.filter_by(_user_id=current_user.id).first()
            cars = Car.query.filter(Car.user_obj.has(account_status=1)).filter_by(_owner=company.id).all()
            print("cars is :", cars)
            response_obj = {
                'status': 'success',
                'cars_list': [car.serialize() for car in cars]
            }
            return response_obj, 200

        except Exception as e:
            print('Exception in company cars list:', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/RegisterDeviceToken')
@com_app.expect(device_token_model)
class RegisterDeviceToken(Resource):
    @company_required
    def post(self):
        data = request.json
        try:
            # check if device is registered before
            token = data.get('device_token')
            user = User.query.filter_by(device_token=token).first()
            if user:
                user.device_token = None
            # set token to current user
            user = User.query.get(current_user.id)
            user.device_token = token
            db.session.commit()
            response_obj = {
                'status': 'success',
                'message': 'Successfully add Device token'
            }
            return response_obj, 201

        except Exception as e:
            print('exception in add device token:', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/CarLocation<id>')
class CarLocation(Resource):
    @company_required
    def get(self, id):
        try:
            car = Car.query.get(id)
            response_obj = {
                'status': 'success',
                'car_location_latitude': car.location_latitude,
                'car_location_longitude': car.location_longitude
            }
            return response_obj, 200

        except Exception as e:
            print('Exception in car location :', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/CarOrders<car_id>')
class CarOrders(Resource):
    @company_required
    def get(self, car_id):
        try:
            orders_id = [row.order_id for row in OrderCarsAndDrivers.query.filter_by(car_id=car_id).all()]
            orders = [Order.query.get(order_id) for order_id in orders_id]
            response_obj = {
                'status': "success",
                'car_orders': [
                    order.serialize_for_company()
                    for order in orders]
            }
            return response_obj, 200
        except Exception as e:
            print("Exception in car orders:", e)
            response_obj = {
                "status": "failed",
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/CompanyProfile')
class CompanyProfile(Resource):
    @company_required
    def get(self):
        try:
            company = Company.query.filter_by(_user_id=current_user.id).first()
            response_obj = {
                'status': "success",
                "company_name": company.name,
                "company_phone": current_user.phone,
                'code': company.id
            }
            return response_obj, 200
        except Exception as e:
            print("Exception in Company profile:", e)
            response_obj = {
                "status": "failed",
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@com_app.route('/NewCar')
class NewCar(Resource):
    @company_required
    def post(self):
        car_user = None
        try:
            role = 4
            data = request.form
            plate_number = data['plate_number']
            car = Car.query.filter_by(number=plate_number).first()
            if car:
                return redirect(url_for('cars_blueprint_company.route_error',
                                        error="Car with entered plate number is already exist"))
            car_type = int(data['car_type'])
            if car_type == 1:
                maktura_plate_number = data["maktura_plate_number"]
            else:
                maktura_plate_number = plate_number
            car_capacity = data['car_capacity']
            car_color = data['car_color']
            doc_img = request.files['doc_image']
            qr_code = Car.generate_qrcode()
            owner = Company.query.filter_by(_user_id=current_user.id).first()
            car_user = User(username=plate_number, email=plate_number, password=qr_code, phone=qr_code[0:11], role=role,
                            account_status=1)
            db.session.add(car_user)
            db.session.commit()
            _, file_extension = os.path.splitext(doc_img.filename)
            url = upload_file_to_s3(doc_img, file_name=plate_number + file_extension, folder='cars_doc')
            new_car = Car(user_id=car_user.id, number=plate_number, owner=owner.id, qr_code=qr_code, _type=car_type,
                          capacity=car_capacity, color=car_color, doc_img=url,
                          maktura_plate_number=maktura_plate_number)
            db.session.add(new_car)
            db.session.commit()
            print(new_car.serialize())
            return redirect(url_for('cars_blueprint_company.company_cars'))
        except Exception as e:
            print("Exception in NewCar: ", e)
            if car_user:
                db.session.delete(car_user)
                db.session.commit()
            return redirect(url_for('cars_blueprint_company.route_error',
                                    error="Some thing Wrong happened, please try again later"))


@com_app.route("/EditCar<car_id>")
class EditCar(Resource):
    @login_required
    def post(self, car_id):
        data = request.form
        car = Car.query.get(car_id)
        car.number = data['plate_number']
        car.color = data['car_color']
        car.capacity = data['car_capacity']
        car._type = int(data['car_type'])
        if int(data['car_type']) == 1:
            maktura_plate_number = data["maktura_plate_number"]
        else:
            maktura_plate_number = data['plate_number']
        car.maktura_plate_number = maktura_plate_number
        doc_img = request.files['doc_image'] or None
        if doc_img:
            _, file_extension = os.path.splitext(doc_img.filename)
            url = upload_file_to_s3(doc_img, file_name=car.number + file_extension, folder='cars_doc')
            car.doc_img = url
        db.session.commit()
        return redirect(url_for("base_blueprint.car_details", id=car_id))


@com_app.route('/DriversList')
class DriversList(Resource):
    @company_required
    def get(self):
        company_id = Company.query.filter_by(_user_id=current_user.id).first().id
        drivers = Driver.query.filter_by(company_id=company_id).filter_by(driver_status=1).all()
        data = {
            'driver_list': [driver.serialize() for driver in drivers]
        }
        return data, 200


@com_app.route('/CompanyDriversList<com_id>')
class companyDriversList(Resource):
    @login_required
    def get(self, com_id):
        company_id = com_id
        drivers = Driver.query.filter_by(company_id=company_id).filter_by(driver_status=1).all()
        data = {
            'driver_list': [driver.serialize() for driver in drivers]
        }
        return data, 200


@com_app.route('/NewDriver')
class NewDriver(Resource):
    @company_required
    def post(self):
        data = request.form
        driver_name = data["driver_name"]
        phone = data["phone"]
        license_number = data["license_number"]
        license_type = data["license_type"]
        img = request.files['license_image']
        company_id = Company.query.filter_by(_user_id=current_user.id).first().id
        driver = Driver.query.filter_by(name=driver_name).first()
        if driver:
            return redirect(
                url_for('driver_blueprint_company.route_error',
                        error=f"FAILED: Driver name: {driver_name} already exist!"))
        driver = Driver.query.filter_by(phone=phone).first()
        if driver:
            return redirect(
                url_for('driver_blueprint_company.route_error', error=f"FAILED: phone: {phone} already exist!"))

        driver = Driver.query.filter_by(license_number=license_number).first()
        if driver:
            return redirect(
                url_for('driver_blueprint_company.route_error',
                        error=f"FAILED: license number: {license_number} already exist!!"))
        _, file_extension = os.path.splitext(img.filename)
        url = upload_file_to_s3(img, file_name=driver_name + file_extension, folder='drivers_license')
        new_driver = Driver(name=driver_name, phone=phone, company_id=company_id, license_number=license_number,
                            license_type=license_type, license_img=url)
        db.session.add(new_driver)
        db.session.commit()
        return redirect(url_for('driver_blueprint_company.index'))


@com_app.route('/ExportCars')
class ExportCars(Resource):
    @company_required
    def get(self):
        company_id = Company.query.filter_by(_user_id=current_user.id).first().id
        job = export_cars.queue(company_id)
        return 200


@com_app.route('/ImportCars')
class ImportCars(Resource):
    @company_required
    def post(self):
        data = request.files['file']
        file_name = data.filename
        file_name = secure_filename(file_name)
        full_path = 'app/utils/uploadedfiles/' + file_name
        data.save(full_path)
        company_id = Company.query.filter_by(_user_id=current_user.id).first().id
        job = import_cars.queue(file_name, company_id)
        return 200


@com_app.route('/DeleteCar<id>')
class DeleteCar(Resource):
    @login_required
    def get(self, id):
        car = Car.query.get(id)
        if car.current_order_id != 0:
            response_obj = {
                "status": "failed",
                "message": "Car assigned to current order, can't be deleted right now"
            }
            return response_obj, 400
        car.user_obj.account_status = -1
        db.session.commit()


@com_app.route('/CarProfile<id>')
class CarProfile(Resource):
    @login_required
    def get(self, id):
        car = Car.query.get(id)
        response_obj = {
            'status': 'success',
            'car_info': [car.serialize()]
        }
        return response_obj, 200


@com_app.route('/CarProfileOrders<car_id>')
class CarProfileOrders(Resource):
    @login_required
    def get(self, car_id):
        orders_id = [x.order_id for x in OrderCarsAndDrivers.query.filter_by(car_id=car_id).all()]
        orders = [Order.query.get(id) for id in orders_id]
        print("orders is ", orders)
        data = {
            'orders_info': [{
                'order_id': order.id,
                'status': order.string_status,
                'num_of_cars': order.num_of_cars
            } for order in orders]
        }
        return data, 200
