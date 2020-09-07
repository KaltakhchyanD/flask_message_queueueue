from flask import Flask, current_app, url_for, redirect

from myapp.config import Config


def create_app():
    app = Flask(__name__)

    config_object = Config()
    app.config.from_object(config_object)



    @app.route("/", methods = ["GET"])
    def index():
        return "Hi"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port = 5000, debug=True)