from flask_login import UserMixin

from app import db, bcrypt, login_manager



class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String(11),unique=True,nullable=False)
    # roles is == > 1 = cars company , 2 = factory , 3 = admin
    role = db.Column(db.Integer, nullable=False, default=1)
    device_token = db.Column(db.String, unique=True)
    hased_password = db.Column(db.String, nullable=False)
    # if user account for factory delegate
    factory = db.relationship('Factory', backref='user', uselist=False)
    company = db.relationship('Company', backref='user', uselist=False)


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

    @property
    def isAdmin(self):
        return True if self.role == 3 else False

    @property
    def isFactory(self):
        return True if self.role == 2 else False

    @property
    def isCompany(self):
        return True if self.role == 1 else False

    def check_password(self, password):
        return bcrypt.check_password_hash(self.hased_password, password)

    def __repr__(self):
        if not self.isAdmin:
            return f"ID: {self.id}, user name: {self.username}, email: {self.email}"

        return f"ID: {self.id}, Admin name: {self.username}"
