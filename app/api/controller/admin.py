import os

import pandas as pd
from flask_login import login_required, current_user
from flask_restplus import Namespace, fields, Resource
from sqlalchemy import func
from werkzeug.utils import secure_filename

from app.api.model.car import Car, available_type
from app.api.model.com import Company
from app.api.model.driver import Driver
from app.api.model.factory import Factory
from app.api.model.order import Order, OrderCarsTypes
from app import db
from app import notf_service
from flask import request, redirect, url_for, make_response, send_file

from app.api.model.order_driver_car import OrderCarsAndDrivers
from app.api.model.user import User

from app.utils.background_jobs import import_factories, import_companies, import_drivers, export_orders, \
    export_companies, export_factories, export_drivers
from app.utils.send_email import pass_mail
from app.utils.upload_images import upload_file_to_s3

admin_app = Namespace('Admin', description='All Admin dashboard related endpoints')


@admin_app.route('/PendingOrders')
class Orders(Resource):
    @login_required
    def get(self):
        print('request for pending prder!')
        if current_user.role != 3:
            response_obj = {
                'status': 'failed',
                'message': "you can't access this Data!"
            }
            return response_obj, 401
        orders = Order.query.filter_by(status=0).all()
        response_obj = {
            'status': 'success',
            'orders-Info': [order.serialize() for order in orders]
        }
        # response_obj = [order.small_serialize() for order in orders]
        return response_obj, 200


@admin_app.route('/InProgressOrders')
class Orders(Resource):
    @login_required
    def get(self):
        if current_user.role != 3:
            response_obj = {
                'status': 'failed',
                'message': "you can't access this Data!"
            }
            return response_obj, 401
        orders = Order.query.filter(5 > Order.status, Order.status > 0).all()
        response_obj = {
            'status': 'success',
            'orders-Info': [order.serialize() for order in orders]
        }
        # response_obj = [order.small_serialize() for order in orders]
        return response_obj,


@admin_app.route('/FinishedOrders')
class Orders(Resource):
    @login_required
    def get(self):
        if current_user.role != 3:
            response_obj = {
                'status': 'failed',
                'message': "you can't access this Data!"
            }
            return response_obj, 401
        orders = Order.query.filter(Order.status == 5).all()
        response_obj = {
            'status': 'success',
            'orders-Info': [order.serialize() for order in orders]
        }
        # response_obj = [order.small_serialize() for order in orders]
        return response_obj, 200


@admin_app.route('/DeleteOrder<order_id>')
class DeleteOrder(Resource):
    @login_required
    def get(self, order_id):
        order_id = order_id  # data['order_id']
        print(order_id)
        if current_user.isCompany:
            response_obj = {
                'status': 'failed',
                'message': "you can't access this Data!"
            }
            return response_obj, 401
        order = Order.query.get(order_id)
        if current_user.isAdmin:
            # set current order to 0 (default value) and status to free for all cars that were assigned to this order
            carsAndDrivers = OrderCarsAndDrivers.query.filter_by(order_id=order_id).all()
            for row in carsAndDrivers:
                car = row.car_opj
                driver = row.driver_opj
                driver.current_order_id = 0  # make driver free
                car.current_order_id = 0
                car._status = 0  # free
            db.session.delete(order)
            db.session.commit()
        else:
            assignedCars = OrderCarsAndDrivers.query.filter_by(order_id=order_id).count()
            if assignedCars:
                response_obj = {
                    'status': 'failed',
                    'message': "Failed: Admin already assigned cars to this order, ask him to cancel your order!"
                }
            return response_obj
        response_obj = {
            'status': 'success'
        }
        return response_obj, 200


@admin_app.route('/FreeCars')
class FreeCars(Resource):
    @login_required
    def get(self):
        try:
            cars = Car.query.filter(Car.user_obj.has(account_status=1), Car._status == 0).all()
            response_obj = {
                'status': 'success',
                'cars_info': [car.serialize() for car in cars]
            }
            return response_obj, 200

        except Exception as e:
            print("Exception in get free cars", e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@admin_app.route('/AssignCarToOrder')
class AssignCarToOrder(Resource):
    @login_required
    def post(self):
        data = request.json
        order_id = data['order_id']
        car_id = data['car_id']
        driver_id = data['driver_id']
        car = Car.query.get(car_id)
        if car._status == 1:
            response_obj = {
                'status': "failed",
                'message': "this car is busy, can't assign it!"
            }
            return response_obj, 400
        order = Order.query.get(order_id)
        num_of_assigned_cars = OrderCarsAndDrivers.query.filter_by(order_id=order_id).count()
        if order.num_of_cars == num_of_assigned_cars:
            response_obj = {
                'status': "failed",
                'message': "all cars needed for this order is already assigned before!"
            }
            return response_obj, 400
        cars_type_count = OrderCarsAndDrivers.query.filter_by(order_id=order_id).filter(
            OrderCarsAndDrivers.car_opj.has(_status=car._type)).count()
        needed_cars_type = OrderCarsTypes.query.filter(OrderCarsTypes.order_id == order_id,
                                                       OrderCarsTypes._type == car._type).first().cars_num
        if cars_type_count == needed_cars_type:
            response_obj = {
                'status': "failed",
                'message': f"Order has enough cars of type: {car.car_type}"
            }
            return response_obj, 400
        new = OrderCarsAndDrivers(order_id=order_id, car_id=car_id, driver_id=driver_id, company_id=car._owner)
        car.current_order_id = order_id
        car.status = 'busy'
        db.session.add(new)
        num_of_assigned_cars = OrderCarsAndDrivers.query.filter_by(order_id=order_id).count()
        if order.num_of_cars == num_of_assigned_cars:
            order.status += 1
        driver = Driver.query.get(driver_id)
        driver.current_order_id = order_id
        db.session.commit()
        # Send notification to truck device
        # TODO remove token
        # device_token = "edbIyzGHfww:APA91bFou5xjZ4DJKTokHzukmpCZmPPlOA13D43MLrMUe41uCesUmcSEP3JWyftR2qNXcTbveDnoJKeigtuM1Y94a5OPxqcGaTdJH-oevIprVgpVz9lXP9GI6ZHivH1-aeDkoyYYl0Zu"  # car.user_obj.device_token
        device_token = car.user_obj.device_token
        message_title = "New Order"
        message_body = "You have new order, click to view details!"
        message_data = {
            'factory_name': order.factory_object.name,
            'notf_type': "new_order",
            "order_id": order.id,
            "pickup_location": {
                'lat': order.from_latitude,
                'lng': order.from_longitude,
                'str': order.pickup_location
            },
            'dropoff_location': {
                'lat': order.to_latitude,
                'lng': order.to_longitude,
                'str': order.dropoff_location
            }
        }
        result = notf_service.notify_single_device(registration_id=device_token, message_title=message_title,
                                                   message_body=message_body, data_message=message_data)

        return 'Car assigned successfully', 200


@admin_app.route('/UnassignedCarFromOrder')
class UnassignedCarFromOrder(Resource):
    @login_required
    def post(self):
        data = request.json
        recored_id = data['id']
        row = OrderCarsAndDrivers.query.get(recored_id)
        car = row.car_opj
        driver_opj = row.driver_opj
        db.session.delete(row)
        car._status = 0
        car.current_order_id = 0
        driver_opj.current_order_id = 0
        order = Order.query.get(row.order_id)
        num_of_assigned_cars = OrderCarsAndDrivers.query.filter_by(order_id=row.order_id).count()
        if order.num_of_cars > num_of_assigned_cars:
            order.status = 0
        db.session.commit()
        return 'success', 200


@admin_app.route('/OrderDetails<id>')
class OrderDetails(Resource):
    @login_required
    def get(self, id):
        order = Order.query.get(id)
        data = {
            'base':
                [{
                    'order_id': id,
                    'status': order.string_status,
                    'date': order.ordered_at.strftime("%A, %d. %B %Y %I:%M %p"),
                    'factory': order.factory_object.name,
                    'pickup': order.pickup_location,
                    'dropoff': order.dropoff_location
                }],
            'assigned_trucks_info': [{
                'driver_name': row.driver_opj.name,
                'driver_phone': row.driver_opj.phone,
                'truck_company': row.car_opj.owner_object.name,
                'plate_no': row.car_opj.number,
                'car_status_for_order': row.string_status,
                'id': row.id,
                'car_id': row.car_id
            } for row in order.cars_and_drivers_object]
        }
        return data, 200


# ----------------- Factory Endpoints --------------


@admin_app.route('/FactoryList')
class FactoryList(Resource):
    @login_required
    def get(self):
        factories = Factory.query.filter(Factory.delegate_opj.has(account_status=1)).all()
        data = {
            'factory_list': [{
                'factory_id': factory.id,
                'name': factory.name,
                'address': factory.address,
                'phone': factory.hotline,
                'num_of_orders': Order.query.filter_by(factory_id=factory.id).count(),
                'logo': factory.logo
            } for factory in factories]
        }

        return data, 200


@admin_app.route('/FactoryProfile<id>')
class FactoryDeatails(Resource):
    @login_required
    def get(self, id):
        factory = Factory.query.get(id)
        data = {
            'factory_info': [{
                'factory_id': factory.id,
                'name': factory.name,
                'phone': factory.hotline,
                'delegate_phone': factory.delegate_opj.phone,
                'email': factory.delegate_opj.email,
                'delegate_name': factory.delegate_opj.username,
                'logo': factory.logo
            }]
        }

        return data, 200


@admin_app.route('/FactoryOrders<id>')
class FactoryOrders(Resource):
    @login_required
    def get(self, id):
        orders = Order.query.filter_by(factory_id=id).all()
        data = {
            'orders_info': [{
                'order_id': order.id,
                'status': order.string_status,
                'num_of_cars': order.num_of_cars,
                'date': order.ordered_at.strftime("%A, %d. %B %Y %I:%M %p")
            } for order in orders]
        }
        return data, 200


@admin_app.route('/DeleteFactory<id>')
class DeleteFactory(Resource):
    def get(self, id):
        factory_current_orders = Order.query.filter_by(factory_id=id).filter(Order.status < 5).count()
        if factory_current_orders:
            resopnse_obj = {
                'status': "failed",
                'message': "this factory has orders not finished right now,Delete it after they finished!"
            }
            return resopnse_obj, 400
        factory = Factory.query.get(id)
        factory.delegate_opj.account_status = -1
        db.session.commit()
        return 'success', 200


@admin_app.route('/NewFactory')
class NewFactory(Resource):
    @login_required
    def post(self):
        data = request.form
        factory_name = data["factory_name"]
        username = data["logistic_name"]
        address = data["address"]
        email = data["email"]
        factory_hotline = data["factory_hotline"]
        delegate_phone = data["delegate_phone"]
        password = "factory"
        img = request.files['factory_logo']
        role = 2
        user = User.query.filter_by(email=email).first()
        if user:
            return redirect(
                url_for('factory_blueprint.route_error', error="FAILED: user with entered E-mail already exist!"))

        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('factory_blueprint.route_error', error="user with entered name already exist!"))

        user = User.query.filter_by(phone=delegate_phone).first()
        if user:
            return redirect(url_for('factory_blueprint.route_error', error="user with entered phone already exist!"))

        user = User(username=username, email=email, role=role, password=password, phone=delegate_phone,
                    account_status=1)
        db.session.add(user)

        fac = Factory.query.filter_by(name=factory_name).first()
        if fac:
            return redirect(url_for('factory_blueprint.route_error', error="factory with entered name already exist!"))

        fac = Factory.query.filter_by(address=address).first()
        if fac:
            return redirect(
                url_for('factory_blueprint.route_error', error="factory with entered address already exist!"))

        fac = Factory.query.filter_by(hotline=factory_hotline).first()
        if fac:
            return redirect(
                url_for('factory_blueprint.route_error', error="factory with entered hot line already exist!"))
        _, file_extension = os.path.splitext(img.filename)
        url = upload_file_to_s3(img, file_name=factory_name + file_extension, folder='factory_logo')
        fac = Factory(name=factory_name, delegate=user.id, address=address, hotline=factory_hotline, logo=url)
        db.session.add(fac)
        db.session.commit()
        return redirect(url_for('factory_blueprint.index'))


@admin_app.route('/PendingFactoryList')
class PendingFactoryList(Resource):
    @login_required
    def get(self):
        factories = Factory.query.filter(Factory.delegate_opj.has(account_status=0)).all()
        data = {
            'factory_list': [{
                'factory_id': factory.id,
                'name': factory.name,
                'address': factory.address,
                'phone': factory.hotline,
                'num_of_orders': Order.query.filter_by(factory_id=factory.id).count(),
                'logo': factory.logo
            } for factory in factories]
        }

        return data, 200


@admin_app.route('/AcceptFactory<id>')
class AcceptFactory(Resource):
    @login_required
    def get(self, id):
        try:
            factory = Factory.query.get(id)
            user = User.query.get(factory._delegate_id)
            print(user)
            user.account_status = 1
            pass_mail(user.temp_pass, user.email, user.username)
            user.temp_pass = "sent"
            db.session.commit()
            return "success", 200

        except Exception as e:
            print("Exception in accept factory: ", e)
            return "Some thong go wrong, please try again later", 500


@admin_app.route('/RefuseFactory<id>')
class RefuseFactory(Resource):
    @login_required
    def get(self, id):
        factory = Factory.query.get(id)
        user = User.query.get(factory._delegate_id)
        db.session.delete(factory)
        db.session.delete(user)
        db.session.commit()
        return "success", 200


@admin_app.route('/ExportFactories')
class ExportFactories(Resource):
    @login_required
    def get(self):
        job = export_factories.queue()
        # job = q.enqueue('app.api.controller.admin.export_factory')

        return 200


@admin_app.route('/ImportFactories')
class ImportFactories(Resource):
    @login_required
    def post(self):
        data = request.files['file']
        file_name = data.filename
        file_name = secure_filename(file_name)
        full_path = 'app/utils/uploadedfiles/' + file_name
        data.save(full_path)
        job = import_factories.queue(file=file_name)
        # job = import_factories.queue(data,file_name)
        return 200


# ----------------- Company Endpoints --------------


@admin_app.route('/CompanyList')
class CompanyList(Resource):
    @login_required
    def get(self):
        companies = Company.query.filter(Company.user_object.has(account_status=1)).all()
        data = {
            'company_list': [{
                'company_id': company.id,
                'name': company.name,
                'address': company.address,
                'phone': User.query.get(company._user_id).phone,
                'logo': company.logo,
                'num_of_orders': 0
            } for company in companies]
        }

        return data, 200


@admin_app.route('/CompanyProfile<id>')
class CompanyDeatails(Resource):
    @login_required
    def get(self, id):
        company = Company.query.get(id)
        data = {
            'company_info': [{
                'company_id': company.id,
                'name': company.name,
                'phone': company.user_object.phone,
                'email': company.user_object.email,
                'delegate_name': company.user_object.username,
                'logo': company.logo
            }]
        }

        return data, 200


@admin_app.route('/CompanyCarsList<id>')
class CompanyCarsList(Resource):
    @login_required
    def get(self, id):
        try:
            cars = Car.query.filter_by(_owner=id).all()
            response_obj = {
                'status': 'success',
                'cars_list': [car.serialize() for car in cars]
            }
            return response_obj, 200

        except Exception as e:
            print("Exception in get CompanyCarsList", e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@admin_app.route('/NewCompany')
class NewCompany(Resource):
    def post(self):
        data = request.form
        company_name = data.get('company_name')
        username = company_name  # data.get('username')
        email = data.get('email')
        password = 'company'  # data.get('password')
        address = data.get('address')
        phone = data.get('company_phone')
        img = request.files['company_logo']
        role = 1
        user = User.query.filter_by(email=email).first()
        if user:
            return redirect(
                url_for('company_blueprint.route_error', error="FAILED: user with entered E-mail already exist!"))

        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(
                url_for('company_blueprint.route_error', error="FAILED: user with entered name already exist!"))

        user = User.query.filter_by(phone=phone).first()
        if user:
            return redirect(
                url_for('company_blueprint.route_error', error="FAILED: user with entered phone already exist!"))

        user = User(username=username, email=email, role=role, password=password, phone=phone)
        db.session.add(user)
        com = Company.query.filter_by(name=company_name).first()
        if com:
            return redirect(
                url_for('company_blueprint.route_error', error="FAILED: company with entered name already exist!"))

        com = Company.query.filter_by(address=address).first()
        if com:
            return redirect(
                url_for('company_blueprint.route_error', error="FAILED: company with entered address already exist!"))
        _, file_extension = os.path.splitext(img.filename)
        url = upload_file_to_s3(img, file_name=company_name + file_extension, folder='company_logo')
        com = Company(name=company_name, account=user.id, address=address, logo=url)
        db.session.add(com)
        db.session.commit()
        return redirect(url_for('company_blueprint.index'))


@admin_app.route('/DeleteCompany<id>')
class DeleteCompany(Resource):
    def get(self, id):
        company = Company.query.get(id)
        # check if this company have any car that in order right now
        busy_cars = Car.query.filter_by(_owner=company.id).filter_by(_status=1).count()
        if busy_cars:
            response_obj = {
                "status": "failed",
                "message": "Company has cars that assigned to order right now, try later after this orders finished!"
            }
            return response_obj, 400
        company.user_object.account_status = -1
        cars = Car.query.filter_by(_owner=company.id).all()
        for car in cars:
            car.user_obj.account_status = -1
        drivers = Driver.query.filter_by(company_id=company.id).all()
        for driver in drivers:
            driver.driver_status = -1
        db.session.commit()
        return 'success', 200


@admin_app.route('/CompanyOrders<id>')
class CompanyOrders(Resource):
    @login_required
    def get(self, id):
        orders_id = [x.order_id for x in
                     OrderCarsAndDrivers.query.filter_by(company_id=id).group_by(OrderCarsAndDrivers.id,
                                                                                 OrderCarsAndDrivers.order_id).all()]
        orders = [Order.query.get(id) for id in orders_id]
        data = {
            'orders_info': [{
                'order_id': order.id,
                'status': order.string_status,
                'num_of_cars': order.num_of_cars,
                'date': order.ordered_at.strftime("%A, %d. %B %Y %I:%M %p")
            } for order in orders]
        }
        return data, 200


@admin_app.route('/PendingCompanyList')
class PendingCompanyList(Resource):
    @login_required
    def get(self):
        companies = Company.query.filter(Company.user_object.has(account_status=0)).all()
        data = {
            'company_list': [{
                'company_id': company.id,
                'name': company.name,
                'address': company.address,
                'phone': company.user_object.phone,
                'logo': company.logo
            } for company in companies]
        }

        return data, 200


@admin_app.route('/AcceptCompany<id>')
class AcceptCompany(Resource):
    @login_required
    def get(self, id):
        try:
            company = Company.query.get(id)
            user = User.query.get(company._user_id)
            user.account_status = 1
            pass_mail(user.temp_pass, user.email, user.username)
            user.temp_pass = "sent"
            db.session.commit()
            return "success", 200
        except Exception as e:
            print("Exception in accept company: ", e)


@admin_app.route('/RefuseCompany<id>')
class RefuseCompany(Resource):
    @login_required
    def get(self, id):
        company = Company.query.get(id)
        user = User.query.get(company._user_id)
        db.session.delete(company)
        db.session.delete(user)
        db.session.commit()
        return "success", 200


@admin_app.route('/ExportCompanies')
class ExportCompanies(Resource):
    @login_required
    def get(self):
        job = export_companies.queue()

        return 200


@admin_app.route('/ImportCompanies')
class ImportCompanies(Resource):
    @login_required
    def post(self):
        data = request.files['file']
        file_name = data.filename
        file_name = secure_filename(file_name)
        full_path = 'app/utils/uploadedfiles/' + file_name
        data.save(full_path)
        job = import_companies.queue(file=file_name)
        return 200


# ----------------- Drivers Endpoints --------------

@admin_app.route('/DriversList')
class DriversList(Resource):
    @login_required
    def get(self):
        drivers = Driver.query.filter_by(driver_status=1).all()
        data = {
            'driver_list': [driver.serialize() for driver in drivers]
        }
        return data, 200


@admin_app.route('/DriverProfile<id>')
class DriverProfile(Resource):
    @login_required
    def get(self, id):
        driver = Driver.query.get(id)
        data = driver.serialize()
        data["license_type"] = driver.license_type
        data = {
            "driver_info": [data]
        }
        return data, 200


@admin_app.route('/DriverOrders<id>')
class CompanyOrders(Resource):
    @login_required
    def get(self, id):
        orders_id = [x.order_id for x in OrderCarsAndDrivers.query.filter_by(driver_id=id).all()]
        orders = [Order.query.get(id) for id in orders_id]
        data = {
            'orders_info': [{
                'order_id': order.id,
                'status': order.string_status,
                'num_of_cars': order.num_of_cars
            } for order in orders]
        }
        return data, 200


@admin_app.route('/NewDriver')
class NewDriver(Resource):
    @login_required
    def post(self):
        data = request.form
        driver_name = data["driver_name"]
        phone = data["phone"]
        license_number = data["license_number"]
        license_type = data["license_type"]
        company_id = data["company_id"]
        img = request.files['license_image']
        driver = Driver.query.filter_by(name=driver_name).first()
        if driver:
            return redirect(
                url_for('driver_blueprint.route_error',
                        error=f"FAILED: Driver name: {driver_name} already exist!"))
        driver = Driver.query.filter_by(phone=phone).first()
        if driver:
            return redirect(
                url_for('driver_blueprint.route_error', error=f"FAILED: phone: {phone} already exist!"))

        driver = Driver.query.filter_by(license_number=license_number).first()
        if driver:
            return redirect(
                url_for('driver_blueprint.route_error',
                        error=f"FAILED: license number: {license_number} already exist!!"))

        company = Company.query.get(company_id)
        if not company:
            return redirect(
                url_for('driver_blueprint.route_error', error=f"FAILED: Company with code: {company_id} not exist!"))
        _, file_extension = os.path.splitext(img.filename)
        url = upload_file_to_s3(img, file_name=driver_name + file_extension, folder='drivers_license')
        new_driver = Driver(name=driver_name, phone=phone, company_id=company_id, license_number=license_number,
                            license_type=license_type, license_img=url)
        db.session.add(new_driver)
        db.session.commit()
        return redirect(url_for('driver_blueprint.index'))


@admin_app.route('/FreeDrivers')
class FreeDrivers(Resource):
    @login_required
    def get(self):
        drivers = Driver.query.filter_by(current_order_id=0).filter_by(driver_status=1).all()
        data = {
            'driver_list': [driver.serialize() for driver in drivers]
        }
        return data, 200


@admin_app.route('/DeleteDriver<id>')
class DeleteDriver(Resource):
    @login_required
    def get(self, id):
        driver = Driver.query.get(id)
        if driver.current_order_id != 0:
            response_obj = {
                "status": "failed",
                "message": "Driver assigned to current order, can't be deleted right now"
            }
            return response_obj, 400
        driver.driver_status = -1
        db.session.commit()


@admin_app.route('/ExportDrivers')
class ExportCompanies(Resource):
    @login_required
    def get(self):
        if current_user.isAdmin:
            job = export_drivers.queue()
        else:
            company_id = Company.query.filter_by(_user_id=current_user.id).first().id
            job = export_drivers.queue(company_id=company_id)
        return 200


@admin_app.route('/ImportDrivers')
class ImportDrivers(Resource):
    @login_required
    def post(self):
        data = request.files['file']
        file_name = data.filename
        file_name = secure_filename(file_name)
        full_path = 'app/utils/uploadedfiles/' + file_name
        data.save(full_path)
        if current_user.isAdmin:
            job = import_drivers.queue(file=file_name)
        else:
            company_id = Company.query.filter_by(_user_id=current_user.id).first().id
            job = import_drivers.queue(file=file_name, company_id=company_id)
        return 200


# ----------------- Orders Endpoints --------------


@admin_app.route('/OrdersList')
class Orders(Resource):
    @login_required
    def get(self):
        if current_user.role != 3:
            response_obj = {
                'status': 'failed',
                'message': "you can't access this Data!"
            }
            return response_obj, 401
        orders = Order.query.all()
        response_obj = {
            'status': 'success',
            'orders_list': [order.serialize() for order in orders]
        }
        return response_obj, 200


@admin_app.route('/NewOrder')
class NewOrder(Resource):
    @login_required
    def post(self):
        try:
            data = request.form
            if current_user.isAdmin:
                factory_id = data['factory_id']
            else:
                factory_id = Factory.query.filter_by(_delegate_id=current_user.id).first().id
            factory = Factory.query.get(factory_id)
            if not factory or factory.delegate_opj.account_status == -1:
                return redirect(
                    url_for('orders_blueprint.route_error', error=f"No Factory exist with ID: {factory_id}"))
            from_latitude = data.get('from_lat')  # دوائر العرض
            from_longitude = data.get('from_lng')  # خطوط الطول
            to_latitude = data.get('to_lat')  # دوائر العرض
            to_longitude = data.get('to_lng')  # خطوط الطول
            pickup_location = data.get('pickup_location')
            dropoff_location = data.get('dropoff_location')
            num_of_trilla = data.get('trilla')
            num_of_maktura = data.get('maktura')
            num_of_cars = int(num_of_maktura) + int(num_of_trilla)
            order = Order(from_latitude=from_latitude, from_longitude=from_longitude, to_latitude=to_latitude,
                          to_longitude=to_longitude, pickup_location=pickup_location, dropoff_location=dropoff_location,
                          factory_id=factory_id, num_of_cars=num_of_cars)
            db.session.add(order)
            db.session.commit()
            for car_type in available_type:
                car = OrderCarsTypes(order_id=order.id, cars_num=data.get(car_type) or 0, car_type=car_type)
                db.session.add(car)
            db.session.commit()
            if current_user.isAdmin:
                return redirect(url_for('orders_blueprint.index'))
            else:
                return redirect(url_for('factoryOrders_blueprint.FactoryOrdersList'))
        except Exception as e:
            print("Exception in NewOrder: ", e)
            if current_user.isAdmin:
                return redirect(
                    url_for('orders_blueprint.route_error', error="Some thing wrong happened please try again later"))
            return redirect(
                url_for('factory_newOrder_blueprint.factory_route_error',
                        error="Some thing wrong happened please try again later"))


@admin_app.route('/ExportOrders')
class ExportOrders(Resource):
    @login_required
    def get(self):
        job = export_orders.queue()
        return 200
