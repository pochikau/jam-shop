from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Product, Order, OrderItem
from decimal import Decimal

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    products = Product.query.filter_by(in_stock=True).all()
    cart = request.args.get("cart", "")
    return render_template("index.html", products=products, cart=cart)


@bp.route("/product/<int:id>")
def product(id):
    p = Product.query.get_or_404(id)
    cart = request.args.get("cart", "")
    return render_template("product.html", product=p, current_cart=cart)


@bp.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "GET":
        return redirect(url_for("main.index"))

    cart = request.form.get("cart")
    if not cart:
        flash("Добавьте товары в корзину.", "warning")
        return redirect(url_for("main.index"))

    # cart format: "id:qty,id:qty"
    items = []
    total = Decimal("0")
    for part in cart.split(","):
        if ":" not in part:
            continue
        pid, qty = part.strip().split(":", 1)
        try:
            pid, qty = int(pid), int(qty)
        except ValueError:
            continue
        if qty < 1:
            continue
        product = Product.query.get(pid)
        if product and product.in_stock:
            price = product.price * qty
            total += price
            items.append((product, qty, product.price * qty))

    if not items:
        flash("Нет товаров для заказа.", "warning")
        return redirect(url_for("main.index"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not email or not address:
        flash("Заполните имя, email и адрес.", "danger")
        return redirect(url_for("main.cart_page", cart=cart))

    order = Order(
        customer_name=name,
        email=email,
        phone=phone,
        address=address,
        total=total,
        status="new",
    )
    db.session.add(order)
    db.session.flush()

    for product, qty, subtotal in items:
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price=subtotal,
            )
        )

    db.session.commit()
    flash("Заказ оформлен. Мы свяжемся с вами по email.", "success")
    return redirect(url_for("main.index"))


@bp.route("/cart")
def cart_page():
    cart = request.args.get("cart", "")
    items = []
    total = Decimal("0")
    for part in cart.split(","):
        if ":" not in part:
            continue
        pid, qty = part.strip().split(":", 1)
        try:
            pid, qty = int(pid), int(qty)
        except ValueError:
            continue
        if qty < 1:
            continue
        product = Product.query.get(pid)
        if product and product.in_stock:
            subtotal = product.price * qty
            total += subtotal
            items.append((product, qty, subtotal))

    return render_template("cart.html", items=items, total=total, cart=cart)
