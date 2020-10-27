import json

from flask import Blueprint, render_template, request, current_app
import redis

from workers import redis_pubsub_worker

blueprint = Blueprint("redis", __name__, url_prefix="")


@blueprint.route("/redis")
def redis_view():
    return render_template("redis_page.html")


@blueprint.route("/redis_create")
def redis_create():
    host = current_app.config["REDIS_HOST"]
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


@blueprint.route("/redis_result")
def redis_check_result():

    host = current_app.config["REDIS_HOST"]
    r = redis.Redis(host=host, port=6379)

    c = redis_pubsub_worker.RedisUniquePubSub(r)
    p = c.subscribe_to_result_once()

    result_message = p.get_message()
    if result_message and result_message["data"] != 1:
        result_dict = json.loads(result_message["data"])
        return {"status": "Finished", "message": result_dict["message"]}, 200
    else:
        return {"status": "Pending"}, 200
