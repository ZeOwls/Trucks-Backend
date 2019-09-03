import pandas as pd

from app import rq, db
from app.api.model.car import Car, available_type
from app.api.model.driver import Driver
from app.api.model.factory import Factory
from app.api.model.user import User
from app.api.model.com import Company
from app.api.model.order import Order

from .send_email import pass_mail
from .send_email import file_mail


@rq.job()
def export_factories():
    from app import app
    with app.app_context():
        print("before factories")
        factories = Factory.query.filter(Factory.delegate_opj.has(account_status=1)).all()
        print(factories)
        f_list = [{
            'ID': factory.id,
            'Name': factory.name,
            'Address': factory.address,
            'Hot line': factory.hotline,
            'username': factory.delegate_opj.username,
            'email': factory.delegate_opj.email,
            'user phone': factory.delegate_opj.phone,

        } for factory in factories]
        df = pd.DataFrame.from_dict(f_list)
        df.to_excel("app/utils/sentfiles/factories.xlsx", encoding='utf8')
        print("sending data via email...")
        file_mail('factories.xlsx', 'factories')
        return 'done'


@rq.job()
def import_factories(file):
    from app import app
    full_path = 'app/utils/uploadedfiles/' + file
    dataFrame = pd.read_excel(full_path)
    length = len(dataFrame)
    with app.app_context():
        for i in range(length):
            row = dataFrame.iloc[i]
            if pd.isna(row['ID']):
                username = str(row['username'])
                email = str(row['email'])
                role = 2
                password = User.generate_pass()
                delegate_phone = str(row['user phone'])
                user = User(username=username, email=email, role=role, password=password, phone=delegate_phone,
                            account_status=1)
                db.session.add(user)
                db.session.commit()
                factory_name = str(row['Name'])
                address = str(row['Address'])
                factory_hotline = str(row['Hot line'])
                fac = Factory(name=factory_name, delegate=user.id, address=address, hotline=factory_hotline)
                db.session.add(fac)
                db.session.commit()
                pass_mail(password, email, username)
    return 200


@rq.job()
def export_companies():
    from app import app
    with app.app_context():
        companies = Company.query.filter(Company.user_object.has(account_status=1)).all()
        c_list = [{
            'ID': company.id,
            'Name': company.name,
            'Address': company.address,
            'Phone': company.user_object.phone,
            'username': company.user_object.username,
            'email': company.user_object.email,
        } for company in companies]
        df = pd.DataFrame.from_dict(c_list)
        df.to_excel("app/utils/sentfiles/companies.xlsx", encoding='utf8')
        file_mail('companies.xlsx', 'companies')
        return 'done'


@rq.job()
def import_companies(file):
    from app import app
    full_path = 'app/utils/uploadedfiles/' + file
    dataFrame = pd.read_excel(full_path)
    length = len(dataFrame)
    with app.app_context():
        for i in range(length):
            row = dataFrame.iloc[i]
            if pd.isna(row['ID']):
                username = str(row['username'])
                email = str(row['email'])
                role = 1
                password = User.generate_pass()
                phone = str(row['Phone'])
                user = User(username=username, email=email, role=role, password=password, phone=phone, account_status=1)
                db.session.add(user)
                db.session.commit()
                company_name = str(row['Name'])
                address = str(row['Address'])
                com = Company(name=company_name, account=user.id, address=address)
                db.session.add(com)
                db.session.commit()
                pass_mail(password, email, username)
    return 200


@rq.job()
def import_drivers(file, company_id=None):
    from app import app
    full_path = 'app/utils/uploadedfiles/' + file
    dataFrame = pd.read_excel(full_path)
    length = len(dataFrame)
    with app.app_context():
        for i in range(length):
            row = dataFrame.iloc[i]
            if pd.isna(row['ID']):
                driver_name = str(row["Name"])
                phone = str(row["Phone"])
                license_number = str(row["License_number"])
                license_type = str(row["License_type"])
                company_id = company_id or int(row["Company_ID"])
                new_driver = Driver(name=driver_name, phone=phone, company_id=company_id, license_number=license_number,
                                    license_type=license_type)
                db.session.add(new_driver)
                db.session.commit()
    return 'done'


@rq.job()
def export_drivers(company_id=None):
    from app import app
    with app.app_context():
        if company_id:
            drivers = Driver.query.filter_by(driver_status=1).filter_by(company_id=company_id).all()
            d_list = [{
                'ID': driver.id,
                'Name': driver.name,
                'Phone': driver.phone,
                'License_number': driver.license_number,
                'License_type': driver.license_type,
            } for driver in drivers]
        else:
            drivers = Driver.query.filter_by(driver_status=1).all()
            d_list = [{
                'ID': driver.id,
                'Name': driver.name,
                'Phone': driver.phone,
                'License_number': driver.license_number,
                'License_type': driver.license_type,
                'Company_Name': driver.company_obj.name,
                'Company_ID': driver.company_obj.id
            } for driver in drivers]
        df = pd.DataFrame.from_dict(d_list)
        df.to_excel('app/utils/sentfiles/drivers.xlsx', encoding='utf8')
        file_mail('drivers.xlsx', 'Drivers')

        return 'done'


@rq.job()
def export_orders():
    from app import app
    with app.app_context():
        orders = Order.query.all()
        o_list = [{
            'ID': order.id,
            'Factory': order.factory_object.name,
            'Pickup location': order.pickup_location,
            'Drop off location': order.dropoff_location,
            'Order status': order.string_status,
            'Number of cars': order.num_of_cars,
            'Ordered at': order.ordered_at
        } for order in orders]
        df = pd.DataFrame.from_dict(o_list)
        df.to_excel('app/utils/sentfiles/orders.xlsx', encoding='utf8')
        file_mail('orders.xlsx', 'Orders')
        return 'done'


@rq.job()
def export_cars(company_id):
    from app import app
    with app.app_context():
        cars = Car.query.filter(Car.user_obj.has(account_status=1)).filter_by(_owner=company_id).all()
        cars_list = [{
            'car_id': car.id,
            'car_plate_number': car.number,
            'car_type': available_type[car._type],
            'car_capacity': car.capacity,
            'car_color': car.color,
        } for car in cars]
        df = pd.DataFrame.from_dict(cars_list)
        df.to_excel('app/utils/sentfiles/cars.xlsx', encoding='utf8')
        file_mail('cars.xlsx', 'Cars')
        return 'done'


@rq.job()
def import_cars(file, company_id):
    from app import app
    with app.app_context():
        full_path = 'app/utils/uploadedfiles/' + file
        dataFrame = pd.read_excel(full_path)
        length = len(dataFrame)
        role = 4
        with app.app_context():
            for i in range(length):
                row = dataFrame.iloc[i]
                if pd.isna(row['car_id']):
                    car_plate_number = str(row["car_plate_number"])
                    car_type = str(row["car_type"])
                    if car_type == "trilla" or car_type == 'تريلا' or car_type == 'تريله' or car_type == "تريلة":
                        car_type = 0
                    else:
                        car_type = 1
                    car_capacity = float(row["car_capacity"])
                    car_color = str(row["car_color"])
                    qr_code = Car.generate_qrcode()
                    car_user = User(username=car_plate_number, email=car_plate_number, password=qr_code,
                                    phone=car_plate_number, role=role,account_status=1)
                    db.session.add(car_user)
                    db.session.commit()
                    new_car = Car(user_id=car_user.id, number=car_plate_number, owner=company_id, qr_code=qr_code,
                                  _type=car_type, capacity=car_capacity, color=car_color)
                    db.session.add(new_car)
                    db.session.commit()
        return 'done'
