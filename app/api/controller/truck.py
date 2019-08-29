from flask_login import login_required, current_user, login_user
from flask import request
from flask_restplus import Namespace, Resource, fields

from app import db, notf_service
from app.api.model.order import Order, OrderHistory
from app.api.model.user import User
from app.api.model.car import Car
from app.api.model.order_driver_car import OrderCarsAndDrivers, orders_status

truck_app = Namespace('Truck', description='All Truck related endpoints')

check_in = truck_app.model('check in', {
    'qr_code': fields.String(required=True, description='truck Qr code '),
    'truck_location_latitude': fields.Float(required=True, description='truck location latitude'),
    'truck_location_longitude': fields.Float(required=True, description='truck location longitude')
})

update_location = truck_app.model('update location', {
    'truck_location_latitude': fields.Float(required=True, description='truck location latitude'),
    'truck_location_longitude': fields.Float(required=True, description='truck location longitude')
})

device_token_model = truck_app.model('assign token to device', {
    'device_token': fields.String(required=True, description='device token')

})

orderStatus_model = truck_app.model('update status of order', {
    'status': fields.Integer(required=True, description='index of order status between 1 and 5 = done')

})


def truck_required(fun):
    def decorator(*args, **kwargs):
        user = User.query.get(current_user.id)
        if not user.isTruck:
            response_obj = {
                'status': 'failed',
                'message': 'you are not a Truck user!'
            }
            return response_obj, 401
        return fun(*args, **kwargs)

    return decorator


@truck_app.route('/CheckIn')
class CheckIn(Resource):
    @truck_app.expect(check_in)
    def post(self):
        data = request.json
        try:
            qr_code = data.get('qr_code')
            car = Car.query.filter_by(qr_code=qr_code).filter(Car.user_obj.has(account_status=1)).first()
            if not car:
                response_obj = {
                    'status': 'failed',
                    'message': 'QR code is wrong'
                }
                return response_obj, 401
            user = User.query.get(car.user_id)
            login_user(user)
            car.location_latitude = data.get('truck_location_latitude')
            car.location_longitude = data.get('truck_location_longitude')
            db.session.commit()
            response_obj = {
                'status': 'success',
                'message': 'Successfully logged in'
            }
            return response_obj, 200
        except Exception as e:
            print('exception in CheckIn Truck:', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@truck_app.route('/UpdateLocation')
class UpdateLocation(Resource):
    @login_required
    @truck_app.expect(update_location)
    @truck_required
    def post(self):
        data = request.json
        try:
            car = Car.query.filter_by(user_id=current_user.id).first()
            car.location_latitude = data.get('truck_location_latitude')
            car.location_longitude = data.get('truck_location_longitude')
            db.session.commit()
            response_obj = {
                'status': 'success',
                'message': 'Successfully Truck location updated',
                'Location': {'location_latitude': car.location_latitude, 'location_longitude': car.location_longitude}
            }
            return response_obj, 200

        except Exception as e:
            print('exception in update Truck location:', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@truck_app.route('/RegisterDeviceToken')
@truck_app.expect(device_token_model)
class RegisterDeviceToken(Resource):
    @login_required
    @truck_required
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


@truck_app.route('/UpdateOrderStatus')
class UpdateOrderStatus(Resource):
    @login_required
    @truck_app.expect(orderStatus_model)
    @truck_required
    def post(self):
        data = request.json
        try:
            car = Car.query.filter_by(user_id=current_user.id).first()  # get current user car
            if not car.current_order_id:
                response_obj = {
                    'status': 'failed',
                    'message': "This truck don't have current order!"
                }
                return response_obj, 400
            order_car_driver = OrderCarsAndDrivers.query.filter_by(order_id=car.current_order_id).filter_by(
                car_id=car.id).first()
            current_status = order_car_driver.status
            if current_status == 5:
                response_obj = {
                    'status': 'failed',
                    'message': "This order is already finished!"
                }
                return response_obj, 400

            new_status = data.get('status')
            if new_status <= current_status:
                response_obj = {
                    'status': 'failed',
                    'message': "new status is less than or equal to current status!"
                }
                return response_obj, 400
            order_car_driver.status = new_status
            db.session.commit()
            # get all cars that assigned to same order, we check all cars status before we update order status
            all_cars = OrderCarsAndDrivers.query.filter_by(order_id=car.current_order_id).all()
            order = Order.query.get(car.current_order_id)
            # check if all cars needed is assigned or not
            if order.num_of_cars == len(all_cars):  # admin not assigned all cars
                final_status = min([x.status for x in all_cars])
                if final_status > order.status:
                    order.status = final_status
                    order_history = OrderHistory(order_id=car.current_order_id, old_state=current_status,
                                                 new_state=new_status)
                    db.session.add(order_history)
                    # TODO remove token
                    # device_token = "edbIyzGHfww:APA91bFou5xjZ4DJKTokHzukmpCZmPPlOA13D43MLrMUe41uCesUmcSEP3JWyftR2qNXcTbveDnoJKeigtuM1Y94a5OPxqcGaTdJH-oevIprVgpVz9lXP9GI6ZHivH1-aeDkoyYYl0Zu"  # car.user_obj.device_token
                    device_token = order.factory_object.delegate_opj.device_token
                    message_title = "Order Status Update"
                    message_body = "Your Order status has been updated,click for details!"
                    message_data = {
                        'order_id': order.id,
                        'notf_type': "order_status_update",

                    }
                    result = notf_service.notify_single_device(registration_id=device_token,
                                                               message_title=message_title,
                                                               message_body=message_body, data_message=message_data)
            if new_status == 5:
                car.status = 'free'
                car.current_order_id = 0
                order_car_driver.driver_opj.current_order_id = None

            # set cars free if order is finished
            # if order.status == 5:
            #     for car in all_cars:
            #         car.status = 'free'
            #         car.current_order_id = 0
            db.session.commit()
            response_obj = {
                'status': 'success',
                'message': f"order status updated successfully from {orders_status[current_status]} to"
                           f" {orders_status[new_status]}"
            }
            return response_obj, 200
        except Exception as e:
            print('Exception in update order status: ', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@truck_app.route('/CarProfile')
class CarProfile(Resource):
    @login_required
    @truck_required
    def get(self):
        try:
            car = Car.query.filter_by(user_id=current_user.id).first()
            response_obj = {
                'status': 'success',
                'Car_info': car.serialize()
            }
            return response_obj, 200
        except Exception as e:
            print('Exception in get car profile: ', e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500


@truck_app.route('/CheckPendingOrder')
class CheckPendingOrder(Resource):
    @login_required
    @truck_required
    def get(self):
        try:
            car = Car.query.filter_by(user_id=current_user.id).first()
            if car.current_order_id == 0:
                response_obj = {
                    'status': 'success',
                    'has_order': "0"
                }
                return response_obj, 200
            order = Order.query.get(car.current_order_id)
            # car status for this order, if car already work on it
            order_status_for_car = "new"
            try:
                current_status = OrderCarsAndDrivers.query.filter_by(order_id=car.current_order_id).filter_by(
                    car_id=car.id).first().status
                order_status_for_car = current_status

            except Exception:
                pass

            response_obj = {
                'status': 'success',
                'has_order': "1",
                'order_status': order.string_status,
                'factory_name': order.factory_object.name,
                'order_id': order.id,
                'pickup_location': order.pickup_location,
                'dropoff_location': order.dropoff_location,
                'from_latitude': order.from_latitude,
                'from_longitude': order.from_longitude,
                'to_latitude': order.to_latitude,
                'to_longitude': order.to_longitude,
                'order_status_for_car': order_status_for_car
            }
            return response_obj, 200
        except Exception as e:
            print("Exception in CheckPendingOrder: ", e)
            response_obj = {
                'status': 'failed',
                'message': 'Something Wrong, please try again later'
            }
            return response_obj, 500
