import json

from celery import Celery
from flask import Flask, current_app, url_for, redirect, render_template, _app_ctx_stack, request
import redis
import pika

from myapp.config import Config
from myapp.utils import RabbitClient
from workers.celery_utils import init_celery
from workers.celery_worker import celery_app, write_task
from workers import celery_worker, redis_pubsub_worker


def create_app():
    app = Flask(__name__)

    config_object = Config()
    app.config.from_object(config_object)

    init_celery(celery_app, app)

    rabbit_host = app.config["RABBIT_HOST"]
    rabbit_user = app.config["RABBIT_USER"]
    rabbit_password = app.config["RABBIT_PASSWORD"]
    rabbit_client = RabbitClient(rabbit_host, rabbit_user, rabbit_password)
    print(f"Rabbit queues names: {rabbit_client.rabbit_queue_list}")

    @app.route("/", methods=["GET"])
    def index():
        print("INDEX")
        return render_template("index.html")

    @app.route("/rabbit")
    def rabbit_view():
        return render_template("rabbit_page.html", queues_names = rabbit_client.rabbit_queue_list)

    @app.route("/rabbit_create", methods = ['POST'])
    def rabbit_create():
        json_from_request = request.get_json()
        rabbit_client.send_message(json_from_request['message'])
        return f"Task started!", 200

    @app.route("/rabbit_result")
    def rabbit_check_result():
        response = rabbit_client.check_response_once()
        print(f"Type of response - {type(response)}")
        if response:
            return {"status": "Finished", "message": response.decode()}, 200
        else:
            return {"status": "Pending"}, 200

    @app.route("/rabbit_result_blocking")
    def rabbit_check_result_blocking():
        response = rabbit_client.check_response_long()
        print(f"Type of response - {type(response)}")
        if response:
            return {"status": "Finished", "message": response.decode()}, 200
        else:
            return {"status": "Pending"}, 200

    @app.route("/redis")
    def redis_view():
        return render_template("redis_page.html")

    @app.route("/redis_create")
    def redis_create():
        host = app.config["REDIS_HOST"]
        r = redis.Redis(host=host, port=6379)

        r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
        # True
        result = r.get("Bahamas")
        # b'Nassau'

        # Subscribe to result_channel b4 send task so rsult can be caught
        c = redis_pubsub_worker.RedisUniquePubSub(r)
        p = c.subscribe_to_result_once()
        print(f"In send - {p}")

        r.publish("my-first-channel", "1 Cool message to publish!")
        # r.publish('my-first-channel', '2 Cool message to publish!')
        # r.publish('my-first-channel', 'And even 3 Cool message to publish!')

        return f"Task started!", 200

    @app.route("/redis_result")
    def redis_check_result():

        host = app.config["REDIS_HOST"]
        r = redis.Redis(host=host, port=6379)

        c = redis_pubsub_worker.RedisUniquePubSub(r)
        p = c.subscribe_to_result_once()

        result_message = p.get_message()
        if result_message and result_message["data"] != 1:
            result_dict = json.loads(result_message["data"])
            return {"status": "Finished", "message": result_dict["message"]}, 200
        else:
            return {"status": "Pending"}, 200

    @app.route("/celery")
    def celery_view():
        write_task.delay("to prinTTT")
        return "Hey celery", 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
