import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
from functools import wraps
from app import db
from app.models import Product, Order, OrderItem


# Простая "заглушка" пользователь для админки (без отдельной таблицы)
class AdminAuth:
    USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    @classmethod
    def check(cls, username, password):
        return username == cls.USERNAME and password == cls.PASSWORD


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not AdminAuth.check(auth.username, auth.password):
            from flask import Response
            return Response(
                "Требуется авторизация",
                401,
                {"WWW-Authenticate": 'Basic realm="Admin"'},
            )
        return f(*args, **kwargs)
    return decorated


class SecureModelView(ModelView):
    def is_accessible(self):
        auth = request.authorization
        return auth and AdminAuth.check(auth.username, auth.password)

    def inaccessible_callback(self, name, **kwargs):
        from flask import Response
        return Response(
            "Требуется авторизация",
            401,
            {"WWW-Authenticate": 'Basic realm="Admin"'},
        )


class ProductView(SecureModelView):
    column_list = ["name", "price", "in_stock", "created_at"]
    column_searchable_list = ["name"]
    column_editable_list = ["price", "in_stock"]
    form_columns = ["name", "description", "price", "image_url", "in_stock"]


class OrderView(SecureModelView):
    column_list = ["id", "customer_name", "email", "total", "status", "created_at"]
    column_searchable_list = ["customer_name", "email"]
    column_editable_list = ["status"]
    form_columns = ["customer_name", "email", "phone", "address", "status"]


class OrderItemView(SecureModelView):
    column_list = ["order_id", "product", "quantity", "price"]


def init_admin(app):
    admin = Admin(app, name="Варенье — Админка", template_mode="bootstrap4", url="/admin")
    admin.add_view(ProductView(Product, db.session, name="Товары"))
    admin.add_view(OrderView(Order, db.session, name="Заказы"))
    admin.add_view(OrderItemView(OrderItem, db.session, name="Позиции заказов"))
