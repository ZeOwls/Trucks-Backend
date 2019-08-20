from functools import wraps
from flask_login import current_user
from flask import current_app

from app.api.model.user import User


def company_required(fun):
    @wraps(fun)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if not user.isCompany:
                return current_app.login_manager.unauthorized()
        else:
            return current_app.login_manager.unauthorized()
        return fun(*args, **kwargs)

    return decorator


def admin_required(fun):
    @wraps(fun)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if not user.isAdmin:
                return current_app.login_manager.unauthorized()
        else:
            return current_app.login_manager.unauthorized()
        return fun(*args, **kwargs)

    return decorator


def factory_required(fun):
    @wraps(fun)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if not user.isFactory:
                return current_app.login_manager.unauthorized()
        else:
            return current_app.login_manager.unauthorized()
        return fun(*args, **kwargs)

    return decorator
