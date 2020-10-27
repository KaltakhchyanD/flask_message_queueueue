from celery import Celery
from flask import Flask, current_app, url_for, redirect, render_template, _app_ctx_stack

from myapp.config import Config
from myapp.utils import RabbitClient
from myapp.redis_views import blueprint as redis_bp
from myapp.celery_views import blueprint as celery_bp

from workers.celery_utils import init_celery
from workers.celery_worker import celery_app

# from workers import celery_worker


def create_app():
    app = Flask(__name__)

    config_object = Config()
    app.config.from_object(config_object)

    # Import here and with context manualy pushed so it can access context
    with app.app_context():
        from myapp.rabbit_views import blueprint as rabbit_bp

    app.register_blueprint(rabbit_bp)
    app.register_blueprint(redis_bp)
    app.register_blueprint(celery_bp)

    init_celery(celery_app, app)

    @app.route("/", methods=["GET"])
    def index():
        print("INDEX")
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
