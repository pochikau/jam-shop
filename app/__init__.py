import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter

db = SQLAlchemy()


def _get_remote_addr():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def _admin_exempt():
    return not request.path.startswith("/admin")


limiter = Limiter(
    key_func=_get_remote_addr,
    application_limits=["10 per minute"],
    application_limits_exempt_when=_admin_exempt,
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///jam.db"
    ).replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        from . import models, routes, admin
        admin.init_admin(app)

    app.register_blueprint(routes.bp, url_prefix="/")

    return app


app = create_app()
