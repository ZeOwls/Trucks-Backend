from app import db

# from .order import Order
from .car import Car
from .driver import Driver

orders_status = ['طلب جديد', 'جاري الوصول لإستلام الشحنة', 'جاري إستلام الشحنة', 'جاري توصيل الشحنة', 'تم الوصول للهدف',
                 'تم توصيل الشحنة بنجاح']


class OrderCarsAndDrivers(db.Model):
    __tablename__ = "orderCarsAndDrivers"
    id = db.Column(db.Integer, primary_key='True')
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    car_opj = db.relationship(Car)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    driver_opj = db.relationship(Driver)
    # from 0 to 5 where 0 == new order and 5 == done
    status = db.Column(db.Integer, nullable=False, default=0)

    def serialize(self):
        # from .order import Order
        # order = Order.query.get(id = self.order_id)
        return {'car_id': self.car_id,
                'status': orders_status[self.status],
                'car_plate_number': self.car_opj.number,
                'car_type': self.car_opj.car_type,
                'driver_id': self.driver_id,
                'driver_name': self.driver_opj.name,
                'driver_phonenumber': self.driver_opj.phone
                }
