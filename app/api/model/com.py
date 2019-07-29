from app import db

# from .user import User
from app.api.model.user import User


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    address = db.Column(db.String, unique=True, nullable=False)
    user_object = db.relationship(User)
    cars = db.relationship('Car', backref='company',  cascade="all,delete")
    drivers = db.relationship('Driver',backref='company', cascade="all,delete")
    @property
    def account(self):
        return self.user_object

    @account.setter
    def account(self, user_id):
        _user = User.query.get(user_id)
        if not _user or not _user.isCompany:
            raise ValueError(f'Invalid Id: {user_id}, user not exist or not company user!')
        self._user_id = user_id

    def __repr__(self):
        return f"ID is : {self.id}, name is {self.name}, Account Info:{self.user_object}"
