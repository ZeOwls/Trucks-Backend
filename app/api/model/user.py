from flask_login import UserMixin

from app import db, bcrypt, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    # roles is == > 1 = cars company , 2 = factory , 3 = admin, 4 = Truck
    role = db.Column(db.Integer, nullable=False, default=1)
    device_token = db.Column(db.String, unique=True)
    account_status = db.Column(db.Integer, nullable=False,
                               default=0)  # 0 = pending admin approve, 1 - Active, -1 = Deleted
    hased_password = db.Column(db.String, nullable=False)
    # if user account for factory delegate
    factory = db.relationship('Factory', backref='user', cascade="all,delete", uselist=False)
    company = db.relationship('Company', backref='user', cascade="all,delete", uselist=False)
    car = db.relationship('Car', backref='user', uselist=False, cascade="all,delete")

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.hased_password = bcrypt.generate_password_hash(password)

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    # @staticmethod

    # @login_manager.unauthorized_handler
    # def unauth_handler():
    #     response_obj = {
    #         'status': 'failed',
    #         'message': 'unauthorized, please log in first'
    #     }
    #     return response_obj, 401

    @property
    def isAdmin(self):
        return True if self.role == 3 else False

    @property
    def isFactory(self):
        return True if self.role == 2 else False

    @property
    def isCompany(self):
        return True if self.role == 1 else False

    @property
    def isTruck(self):
        return True if self.role == 4 else False

    def check_password(self, password):
        return bcrypt.check_password_hash(self.hased_password, password)

    def __repr__(self):
        if not self.isAdmin:
            return f"ID: {self.id}, user name: {self.username}, email: {self.email}"

        return f"ID: {self.id}, Admin name: {self.username}"
