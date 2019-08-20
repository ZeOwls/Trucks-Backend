import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from dotenv import load_dotenv

from app import app as application, db

from app.api.model.factory import Factory

manager = Manager(application)
migrate = Migrate(application, db)
manager.add_command('db', MigrateCommand)



@manager.command
@manager.option('-p', '--port', help='app:app port, default=5000')
def run(port=5000):
    # ip = socket.gethostbyname(socket.getfqdn())
    # host = os.environ.get('IP', ip)
    port = int(os.environ.get('PORT', 5000))
    load_dotenv('./.env')
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
    #     ['car4', 1, Car.generate_qrcode(), 'trilla', 15,"ازرق"],
    #     ['car5', 2, Car.generate_qrcode(), 'maktura', 15,"ابيض"],
    #     ['car6', 2, Car.generate_qrcode(), 'maktura', 15,"اسود"],
    #     ['car7', 2, Car.generate_qrcode(), 'maktura', 15,"ابيض"],
    #     ['car8', 2, Car.generate_qrcode(), 'maktura', 15,"اخضر"],
    # ]
    # role = 4
    # for car in cars:
    #     car_user = User(username=car[0], email=car[0], password=car[2], phone=car[0], role=role)
    #     db.session.add(car_user)
    #     db.session.commit()
    #     new_car = Car(user_id=car_user.id, number=car[0], owner=car[1], qr_code=car[2], car_type=car[3],
    #                   capacity=car[4],color=car[5])
    #     db.session.add(new_car)
    #     db.session.commit()

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
    # new = OrderCarsAndDrivers(order_id=25,car_id=2,driver_id=2)
    # car = Car.query.get(2)
    # car.current_order_id = 25
    # car.status = 'busy'
    # db.session.add(new)
    # db.session.commit()
    ###################################3
    # add admin account
    # admin = User(username='Admin',email="admin@test.com",phone="01200",role=3,password="admin")
    # db.session.add(admin)
    # db.session.commit()
    # import pandas as pd
    # factories = Factory.query.all()
    # f_list = [{
    #     'ID': factory.id,
    #     'Name': factory.name,
    #     'Hot line': factory.hotline,
    #     'username': factory.delegate_opj.username,
    #     'email': factory.delegate_opj.email,
    #     'user phone': factory.delegate_opj.phone
    # } for factory in factories]
    # df = pd.DataFrame.from_dict(f_list)
    # df.to_csv('file1.csv')

    pass


if __name__ == "__main__":
    manager.run()
