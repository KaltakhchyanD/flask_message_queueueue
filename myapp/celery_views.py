from flask import Blueprint, render_template, request, current_app

from workers.celery_worker import write_task, dummy_task
from workers.celery_utils import CeleryClient

blueprint = Blueprint("celery", __name__, url_prefix="")

task_id_async_result_dict = {}

celery_client = CeleryClient()
celery_app = celery_client.make_celery("myapp")
celery_client.init_celery(celery_app, current_app)

@blueprint.route("/celery")
def celery_view():
    return render_template("celery_page.html")


@blueprint.route("/celery_create_task", methods=["POST"])
def run_task():
    task_json = request.get_json()

    if (
        "message" not in task_json.keys()
        or "quantity" not in task_json.keys()
        or "priority" not in task_json.keys()
        or "task_id" not in task_json.keys()
    ):
        return (
            {
                "error_code": 1,
                "error_message": "task_json should contain 'message', 'quantity', 'priority' and 'task_id' ",
            },
            400,
        )

    if not task_json["quantity"]:
        return {"error_code": 2, "error_message": "quantity should not be empty"}, 400
    elif not task_json["quantity"].isdigit():
        return {"error_code": 3, "error_message": "quantity should be digits"}, 400
    elif not int(task_json["quantity"]) > 0:
        return {"error_code": 4, "error_message": "quantity should more then 0"}, 400

    if not task_json["priority"]:
        return {"error_code": 5, "error_message": "priority should not be empty"}, 400
    elif not task_json["priority"].isdigit():
        return {"error_code": 6, "error_message": "priority should be digit"}, 400
    elif not 0 < int(task_json["priority"]) < 4:
        return (
            {"error_code": 7, "error_message": "priority should between 1 and 3"},
            400,
        )

    if not task_json["task_id"]:
        return {"error_code": 8, "error_message": "task_id should not be empty"}, 400

    async_result = dummy_task.delay(task_json)
    task_id_async_result_dict[task_json["task_id"]] = async_result

    print("Started celery task")
    return "<h1>Started celery task</h1>"


@blueprint.route("/celery_check_result", methods=["POST"])
def check_task_result():
    task_json = request.get_json()

    if "task_id" not in task_json.keys():
        return (
            {"error_code": 10, "error_message": "task_json should contain 'task_id' "},
            400,
        )

    if not task_json["task_id"]:
        return {"error_code": 11, "error_message": "task_id should not be empty"}, 400

    try:
        async_result_to_check = task_id_async_result_dict[task_json["task_id"]]
    except KeyError:
        return {"error_code": 12, "error_message": f"task_id {task_json['task_id']} is not known to server"}, 500


    if async_result_to_check.ready():
        message = async_result_to_check.get()
        result_json = {"status": "Ready", "message": message}
    else:
        result_json = {"status": "Pending", "message": "garbage"}

    return result_json, 200
