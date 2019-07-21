import uuid
from app import db

# from .company import Company
# from .order_driver_car import OrderCarsAndDrivers

# if we want to add new status we just add it in this list
# NOTE : we mapped status to it's index when we store it in database
from app.api.model.com import Company

available_status = ['free', 'busy']

# if we want to add new type we just add it in this list
# NOTE : we mapped status to it's index when we store it in database
available_type = ['trilla', 'maktura']


class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    capacity = db.Column(db.Float, nullable=False)
    location_latitude = db.Column(db.Float)
    # location_x = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    # location_y = db.Column(db.Float)
    _owner = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    owner_object = db.relationship(Company)
    qr_code = db.Column(db.String, unique=True, nullable=False)
    _status = db.Column(db.Integer, nullable=False, default=0)  # 0 == free , 1 == busy
    _type = db.Column(db.Integer, nullable=False)  # 0 == trilla , 1 == maktura
    orders = db.relationship('OrderCarsAndDrivers', backref='car',  cascade="all,delete")
    current_order_id = db.Column(db.Integer,default=0)
    @property
    def owner(self):
        return self.owner_object

    @owner.setter
    def owner(self, owner_id):
        company = Company.query.get(owner_id)
        if not company:
            raise ValueError(f'Invalid company ID: {owner_id}.')
        else:
            self._owner = owner_id

    @property
    def status(self):
        return available_status[self._status]

    @status.setter
    def status(self, state):
        if state.lower() in available_status:
            self._status = available_status.index(state.lower())
        else:
            raise ValueError(
                f"Status can't be {state}, available status is {available_status}")

    @property
    def car_type(self):
        return available_type[self._type]

    @car_type.setter
    def car_type(self, typ):
        if typ.lower() in available_type:

            self._type = available_type.index(typ.lower())
        else:
            raise ValueError(
                f"{typ} not avilable car type, Avilable types is :{available_type}")

    def __repr__(self):
        return f"Car NO.:{self.number}, type: {self.car_type}, locatios is :{(self.location_latitude,self.location_longitude)}" \
               f" status:{available_status[self._status]},'Owner INFO:{self.owner_object}"

    @staticmethod
    def generate_qrcode():
        return str(uuid.uuid4())

    def serialize(self):
        from app.api.model.order_driver_car import OrderCarsAndDrivers
        order = OrderCarsAndDrivers.query.filter_by(order_id=self.current_order_id).filter_by(car_id=self.id).first()
        return {
            'car_id': self.id,
            'car_plate_number': self.number,
            'car_type': available_type[self._type],
            'location': {
                'location_latitude': self.location_latitude,
                'location_longitude': self.location_longitude
            },
            'car_status': self.status,
            'Current_order_id:': self.current_order_id if self.current_order_id !=0 else "Car is free right now"
        }
