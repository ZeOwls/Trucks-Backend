from app import db

# from .order import Order
from .car import Car
from .driver import Driver


class OrderCarsAndDrivers(db.Model):
    __tablename__ = "orderCarsAndDrivers"
    id = db.Column(db.Integer, primary_key='True')
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    car_opj = db.relationship(Car)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    driver_opj = db.relationship(Driver)

    def serialize(self):
        return {'car_id': self.car_id,
                'car_plate_number': self.car_opj.number,
                'car_type': self.car_opj.car_type,
                'driver-id': self.driver_id,
                'driver_name': self.driver_opj.name,
                'driver_phonenumber': self.driver_opj.phone}
