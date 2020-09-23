import json

from celery import Celery
from flask import Flask, current_app, url_for, redirect, render_template, _app_ctx_stack
import redis
import pika

from myapp.celery_utils import celery_app, init_celery
from myapp.config import Config
from workers.celery_worker import write_task
from workers import celery_worker, redis_pubsub_worker




def create_app():
    app = Flask(__name__)

    config_object = Config()
    app.config.from_object(config_object)

    init_celery(celery_app, app)

    @app.route("/", methods=["GET"])
    def index():
        print("INDEX")
        return render_template("index.html")

    @app.route("/rabbit")
    def rabbit_view():
        credentials = pika.PlainCredentials("rabbit", "mq")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbit", credentials=credentials)
        )

        channel = connection.channel()

        channel.queue_declare(queue="hello", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="hello",
            body="Hello World!",
            properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
        )
        print(" [x] Sent 'Hello World!'")
        connection.close()

        return "Hey", 200

    @app.route("/redis")
    def redis_view():
        r = redis.Redis(host="redis", port=6379)
        #r = redis.Redis(host="localhost", port=6379)
        r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
        # True
        result = r.get("Bahamas")
        # b'Nassau'

        # Subscribe to result_channel b4 send task so rsult can be caught
        c = redis_pubsub_worker.RedisUniquePubSub(r)
        p = c.subscribe_to_result_once()
        print(f'In send - {p}')



        r.publish('my-first-channel', '1 Cool message to publish!')
        r.publish('my-first-channel', '2 Cool message to publish!')
        r.publish('my-first-channel', 'And even 3 Cool message to publish!')

        return f'Hey redis - {result}', 200

    @app.route('/redis_result')
    def redis_check_result():
        r = redis.Redis(host="redis", port=6379)

        c = redis_pubsub_worker.RedisUniquePubSub(r)
        p = c.subscribe_to_result_once()
        print(f'In result - {p}')


        result_message = p.get_message()
        if result_message:
            print(f"{result_message['data']}")
            result_dict = json.loads(result_message['data']) if result_message['data']!=1 else {'message':'some_other'}
            return {'status':'Finished', 'message' : result_dict['message']}, 200
        else:
            return {'status':'Pending'}, 200


    @app.route("/celery")
    def celery_view():
        write_task.delay("to prinTTT")
        return "Hey celery", 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
