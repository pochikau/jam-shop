from flask import render_template
from flask_limiter.exceptions import RateLimitExceeded


def register_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    @app.errorhandler(RateLimitExceeded)
    def rate_limit_exceeded(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500
