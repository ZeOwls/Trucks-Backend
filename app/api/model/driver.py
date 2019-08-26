from app import db

# from .order_driver_car import OrderCarsAndDrivers
from app.api.model.com import Company


class Driver(db.Model):
    __tablename__ = "driver"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    license_number = db.Column(db.String, nullable=False)
    license_type = db.Column(db.String, nullable=False)
    license_img = db.Column(db.String, nullable=False)
    company_obj = db.relationship(Company)
    driver_status = db.Column(db.Integer, default=1, nullable=False)  # 1 - Active, -1 - Deleted
    current_order_id = db.Column(db.Integer, db.ForeignKey('order.id'), default=0)
    orders = db.relationship('OrderCarsAndDrivers', backref='driver', cascade="all,delete", uselist=False)

    def __repr__(self):
        return f"ID :{self.id}, name:{self.name}, phone:{self.phone}"

    def serialize(self):
        from .order_driver_car import OrderCarsAndDrivers
        return {
            'driver_id': self.id,
            'name': self.name,
            'phone': self.phone,
            'company_name': self.company_obj.name,
            'num_of_orders': OrderCarsAndDrivers.query.filter_by(driver_id=self.id).count(),
            'license_img': self.license_img
        }
