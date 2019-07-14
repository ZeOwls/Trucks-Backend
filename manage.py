import os
import socket

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app as application, db
from app.api import blueprint as api_bl

# import app.api.model
# from app.api.model.car import Car
# from app.api.model.company import Company
# from app.api.model.user import User
from app.api.model.car import Car
from app.api.model.order_driver_car import OrderCarsAndDrivers

manager = Manager(application)
migrate = Migrate(application, db)
manager.add_command('db', MigrateCommand)

# register blueprints
application.register_blueprint(api_bl)


@manager.command
@manager.option('-p', '--port', help='app:app port, default=5000')
def run(port=5000):
    # ip = socket.gethostbyname(socket.getfqdn())
    # host = os.environ.get('IP', ip)
    port = int(os.environ.get('PORT', 5000))
    application.run(port=port)


@manager.command
def insertData():
    # insert users
    from app.api.model.user import User
    # users = [{'username': 'factory', 'email': 'factory@test.com', 'password': 'factory', 'role': 2,'phone':123},
    #          {'username': 'admin', 'email': 'admin@test.com', 'password': 'admin', 'role': 3,'phone':1234},
    #          {'username': 'company', 'email': 'company@test.com', 'password': 'company', 'role': 1,'phone':1235}, ]
    # for user in users:
    #     user = User(username=user['username'],email=user['email'],password=user['password'],role=user['role']
    #                 ,phone=user['phone'])
    #     db.session.add(user)
    #     db.session.commit()
    # users = User.query.all()
    # print('users is :',users)

    ####################################################
    # insert factory
    # name = '7ded and solb'
    # delegate = 1
    # address = '5 shar3 nassar'
    # hotline = "01255"
    # from app.api.model.factory import Factory
    # fac = Factory(name=name,delegate=delegate,address=address,hotline=hotline)
    # db.session.add(fac)
    # db.session.commit()
    # facts = Factory.query.all()
    # print(facts)
    ###################################################

    # insert company
    from app.api.model.com import Company
    #
    # try:
    #     comp = Company(name='new company', account=3,address='5 wall st')
    #     db.session.add(comp)
    #     db.session.commit()
    # except Exception as e:
    #     # traceback.print_exc()
    #     print("Exceptions is :", e)
    # comps = Company.query.all()
    # print(comps)

    #############################################
    # insert cars to company
    # cars = [
    #     ['car1', 1, Car.generate_qrcode(), 'trilla', 15],
    #     ['car2', 1, Car.generate_qrcode(), 'maktura', 15]]
    # role = 4
    # for car in cars:
    #     car_user = User(username=car[0], email=car[0], password=car[2], phone=car[0], role=role)
    #     db.session.add(car_user)
    #     db.session.commit()
    #     new_car = Car(user_id=car_user.id, number=car[0], owner=car[1], qr_code=car[2], car_type=car[3],
    #                   capacity=car[4])
    #     db.session.add(new_car)
    #     db.session.commit()
    #
    # cars = Car.query.all()
    # [print(car) for car in cars]
    ##############################################
    # inser drivers
    # drivers = [['ahmed','01203000270'],['ayman','01203050270'],['osama','01201000270']]
    # from app.api.model.driver import Driver
    # for driver in drivers:
    #     d = Driver(name=driver[0],phone=driver[1])
    #     db.session.add(d)
    #
    # db.session.commit()
    # drivers = Driver.query.all()
    # print(drivers)
    ###########################################
    # inser orders
    # from app.api.model.order import Order
    # order = Order(from_latitude=1,from_longitude=2,to_latitude=6,to_longitude=7,pickup_location='ayman ST',
    #               dropoff_location='ahmed ST', factory_id=1,num_of_cars=5)
    # db.session.add(order)
    # db.session.commit()
    # orders = Order.query.all()
    # print(orders)
    #####################################33
    # assign driver and car for order
    new = OrderCarsAndDrivers(order_id=2,car_id=1,driver_id=2)
    car = Car.query.get(1)
    car.current_order_id=2
    db.session.add(new)
    db.session.commit()
    # pass


if __name__ == "__main__":
    manager.run()
