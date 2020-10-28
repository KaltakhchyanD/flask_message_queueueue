from flask import Blueprint, render_template, request, current_app

from myapp.utils import RabbitClient

blueprint = Blueprint("rabbit", __name__, url_prefix="")

rabbit_host = current_app.config["RABBIT_HOST"]
rabbit_user = current_app.config["RABBIT_USER"]
rabbit_password = current_app.config["RABBIT_PASSWORD"]
rabbit_client = RabbitClient(rabbit_host, rabbit_user, rabbit_password)
print(f"Rabbit queues names: {rabbit_client.rabbit_queue_list}")


@blueprint.route("/rabbit")
def rabbit_view():
    return render_template(
        "rabbit_page.html", queues_names=rabbit_client.rabbit_queue_list
    )


@blueprint.route("/rabbit_create", methods=["POST"])
def rabbit_create():
    json_from_request = request.get_json()
    rabbit_client.send_message(
        json_from_request["message"], json_from_request["task_id"]
    )
    return f"Task started!", 200


@blueprint.route("/rabbit_result")
def rabbit_check_result():
    response = rabbit_client.check_response_once()
    print(f"Type of response - {type(response)}")
    if response:
        return (
            {
                "status": "Finished",
                "message": response["body"].decode(),
                "task_id": response["task_id"],
            },
            200,
        )
    else:
        return {"status": "Pending"}, 200


@blueprint.route("/rabbit_result_blocking")
def rabbit_check_result_blocking():
    response = rabbit_client.check_response_long()
    print(f"Type of response - {type(response)}")
    if response:
        return (
            {
                "status": "Finished",
                "message": response["body"].decode(),
                "task_id": response["task_id"],
            },
            200,
        )
    else:
        return {"status": "Pending"}, 200
