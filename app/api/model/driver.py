from app import db


# from .order_driver_car import OrderCarsAndDrivers


class Driver(db.Model):
    __tablename__ = "driver"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    orders = db.relationship('OrderCarsAndDrivers', backref='driver', uselist=False)

    def __repr__(self):
        return f"ID :{self.id}, name:{self.name}, phone:{self.phone}"
