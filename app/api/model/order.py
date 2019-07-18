from app import db
from datetime import datetime
import time
from flask_login import current_user

from .factory import Factory
from .car import available_type
from .order_driver_car import OrderCarsAndDrivers

# from .order_driver_car import OrderCarsAndDrivers

orders_status = ['طلب جديد', 'جاري الوصول لإستلام الشحنة', 'جاري إستلام الشحنة', 'جاري توصيل الشحنة', 'تم الوصول للهدف',
                 'تم توصيل الشحنة بنجاح']


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_latitude = db.Column(db.Float, nullable=False)
    from_longitude = db.Column(db.Float, nullable=False)
    to_latitude = db.Column(db.Float, nullable=False)
    to_longitude = db.Column(db.Float, nullable=False)
    pickup_location = db.Column(db.String, nullable=False)
    dropoff_location = db.Column(db.String, nullable=False)
    factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False)
    factory_object = db.relationship(Factory)
    # from 0 to 5 where 0 == new order and 5 == done
    status = db.Column(db.Integer, nullable=False, default=0)
    ordered_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    num_of_cars = db.Column(db.Integer, nullable=False)
    history = db.relationship('OrderHistory', backref='order', cascade="all,delete")
    cars_type = db.relationship('OrderCarsTypes', backref='order',  cascade="all,delete")
    cars_and_drivers = db.relationship('OrderCarsAndDrivers', backref='order',  cascade="all,delete")

    def small_serialize(self):
        print("here")
        print(self.id)
        return {'order_number': self.id,
                'order_status': orders_status[self.status],
                'order_date': time.mktime(self.ordered_at.timetuple()),
                'cars_number': self.num_of_cars
                }

    def serialize(self):
        cars_type = OrderCarsTypes.query.filter_by(order_id=self.id).all()
        cars_type = [car.serialize() for car in cars_type]
        cars_and_drivers = OrderCarsAndDrivers.query.filter_by(order_id=self.id).all()
        cars_and_drivers = [car_and_driver.serialize() for car_and_driver in cars_and_drivers]
        assigned_trucks = OrderCarsAndDrivers.query.filter_by(order_id=self.id).count()
        return {'order_number': self.id,
                'order_status': orders_status[self.status],
                'order_date':time.mktime(self.ordered_at.timetuple()),
                'from': {'latitude': self.from_latitude, 'longitude': self.from_longitude,
                         'address': self.pickup_location},
                'to': {'latitude': self.to_latitude, 'longitude': self.to_longitude, 'address': self.dropoff_location},

                'num_of_cars': self.num_of_cars,
                'cars_type_info': cars_type,
                'drivers_cars_info': cars_and_drivers,
                'factory_name': self.factory_object.name,
                'assigned_trucks': assigned_trucks if current_user.role == 3 else ""
                }

    def __repr__(self):
        return f"id:{self.id}, From:{(self.from_latitude,self.from_longitude)}, To:{(self.to_latitude,self.to_longitude)}" \
               f"status:{self.status}, order at:{self.ordered_at}, Factory:{self.factory_object}" \
               f" num of cars:{self.num_of_cars}"


class OrderHistory(db.Model):
    __tablename__ = "orderHistory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    # from 0 to 4 where 0 == new order and 4 == جاري التسليم
    old_state = db.Column(db.Integer, nullable=False, default=0)
    # from 1 to 5 where 0 == في الطريق الي نقطة الاستلام and 5 == done
    new_state = db.Column(db.Integer, nullable=False, default=1)
    changed_on = db.Column(db.DateTime, nullable=False, default=datetime.now())


class OrderCarsTypes(db.Model):
    __tablename__ = "orderCarsTypes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    cars_num = db.Column(db.Integer, nullable=False, default=0)
    _type = db.Column(db.Integer, nullable=False)  # 0 == trilla , 1 == maktura

    @property
    def car_type(self):
        return available_type[self._type]

    def serialize(self):
        return {available_type[self._type]: self.cars_num}

    @car_type.setter
    def car_type(self, typ):
        if typ.lower() in available_type:
            self._type = available_type.index(typ.lower())
        else:
            raise ValueError(
                f"{typ} not available car type, Available types is :{available_type}")
