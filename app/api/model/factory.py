from app import db

# from .user import User
from app.api.model.user import User


class Factory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.String(255),unique=True,nullable=False)
    hotline = db.Column(db.String,unique=True,nullable=False)
    _delegate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    delegate_opj = db.relationship(User)
    orders = db.relationship('Order', backref='factory',  cascade="all,delete")

    @property
    def delegate(self):
        return self._delegate_id

    @delegate.setter
    def delegate(self, user_id):
        user = User.query.get(user_id)
        if not user or not user.isFactory:
            raise ValueError(f'Invalid Id: {user_id}, user not exist or not factory user!')
        self._delegate_id = user_id

    def __repr__(self):
        user = User.query.get(self._delegate_id)
        return f"Factory name is : {self.name},account : {user}"