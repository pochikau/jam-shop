import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, session, render_template, flash
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


class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get("is_admin") is True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_login"))


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

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if AdminAuth.check(username, password):
                session["is_admin"] = True
                flash("Добро пожаловать в админку.", "success")
                return redirect(url_for("admin.index"))
            flash("Неверный логин или пароль.", "danger")
        return render_template("admin_login.html")

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("is_admin", None)
        flash("Вы вышли из админки.", "success")
        return redirect(url_for("main.index"))
