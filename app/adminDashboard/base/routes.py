import time
import locale

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.adminDashboard.base import blueprint, factory_blueprint, root
from app.adminDashboard.base.forms import LoginForm, CreateAccountForm
from app.api.model.com import Company
from app.api.model.factory import Factory
from app.api.model.user import User
from app.api.model.order import Order
from app.utils.login import company_required, factory_required
from . import company_blueprint

# locale.setlocale(locale.LC_ALL, "en_EG.utf8")
from app.utils.login import admin_required


@root.route('/')
def root_index():
    return redirect(url_for('base_blueprint.route_default'))


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
    return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))


# Login & Registration


@blueprint.route('/login<message>', methods=['GET', 'POST'])
@blueprint.route('/login', methods=['GET', 'POST'])
def login(message=""):
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'login' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.isAdmin:
            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))
        return render_template('errors/page_403.html')
    if not current_user.is_authenticated:
        return render_template(
            'login/login.html',
            login_form=login_form,
            create_account_form=create_account_form,
            message=message
        )
    if current_user.isAdmin:
        return redirect(url_for('home_blueprint.index'))

    if current_user.isCompany:
        return redirect(url_for('home_blueprint_company.company_index'))

    if current_user.isFactory:
        return redirect(url_for('home_blueprint_factory.factory_index'))


@blueprint.route('/create_user', methods=['POST'])
def create_user():
    user = User(**request.form)
    db.session.add(user)
    db.session.commit()
    return jsonify('success')


# ------------------ Order Endpoints ---------------------

@blueprint.route('/OrderDetailsPage<id>')
@login_required
def order_datails(id):
    order = Order.query.get(id)
    data = {
        'order_id': id,
        'order_status': order.status,
        'from_latitude': order.from_latitude,
        'from_longitude': order.from_longitude
    }
    return render_template('order_details.html', data=data), 200


@blueprint.route('/EditOrder<id>')
@login_required
def edit_order(id):
    order = Order.query.get(id)
    data = {
        'pickup': order.pickup_location,
        'dropoff': order.dropoff_location,
        'assigned_trucks_info': [{
            'driver_name': row.driver_opj.name,
            'driver_phone': row.driver_opj.phone,
            'truck_company': row.car_opj.owner_object.name,
            'plate_no': row.car_opj.number,
            'car_status_for_order': row.status
        } for row in order.cars_and_drivers_object]
    }
    return render_template('order_details.html', data=data), 200


@blueprint.route('/assignCarToOrder<order_id><car_id>')
@admin_required
def assignCarToOrder(order_id, car_id):
    print("in routes")
    data = {
        'order_id': order_id,
        'car_id': car_id
    }
    return render_template('assign_car_to_order.html', data=data), 200


# -------------------- Factory Endpoints ---------------------


@blueprint.route('/FactoryDetailsPage<id>')
@admin_required
def factory_datails(id):
    data = {
        'factory_id': id
    }
    return render_template('factory_details.html', data=data), 200


@blueprint.route('/SignupFactory<error>')
@blueprint.route('/SignupFactory')
def SignupFactory(error=""):
    return render_template('./login/signup_factory.html', error=error), 200


@factory_blueprint.route('/')
@factory_required
def FactoryOrdersList(message=""):
    factory_id = Factory.query.filter_by(_delegate_id=current_user.id).first().id
    data = {
        'factory_id': factory_id
    }
    return render_template('factory_details.html', data=data), 200


@factory_blueprint.route('/NewOrder')
@factory_required
def new_order():
    return render_template('NewOrder.html'), 200


# -------------------- Company Endpoints ---------------------


@blueprint.route('/CompanyDetailsPage<id>')
@admin_required
def company_details(id):
    data = {
        'company_id': id
    }
    return render_template('company_details.html', data=data), 200


@blueprint.route('/CarProfile<id>')
@login_required
def car_details(id):
    data = {
        'car_id': id
    }
    return render_template('car_profile.html', data=data), 200


@blueprint.route('/SignupCompany<error>')
@blueprint.route('/SignupCompany')
def SignupCompany(error=""):
    return render_template('./login/signup_company.html', error=error), 200


@company_blueprint.route('/')
@company_required
def CompanyOrdersList():
    company_id = Company.query.filter_by(_user_id=current_user.id).first().id
    data = {
        'company_id': company_id
    }
    return render_template('company_details.html', data=data), 200


# -------------------- Driver Endpoints ---------------------


@blueprint.route('/DriverDetailsPage<id>')
@login_required
def driver_details(id):
    data = {
        'driver_id': id
    }
    return render_template('driver_details.html', data=data), 200


# ------------------------------------------------------------

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


## Errors


@login_manager.unauthorized_handler
def unauthorized_handler():
    if request.is_xhr:
        response_obj = {
            'status': 'failed',
            'message': 'unauthorized, please log in first'
        }
        return response_obj, 403

    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/page_404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/page_500.html'), 500
