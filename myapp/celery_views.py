from flask import Blueprint, render_template, request, current_app

from workers.celery_worker import write_task, dummy_task

blueprint = Blueprint("celery", __name__, url_prefix="")


@blueprint.route("/celery")
def celery_view():
    write_task.delay("to prinTTT")
    return "Hey celery", 200


@blueprint.route("/celery_task")
def run_task():
    dummy_task_json = {"task_id": "1234", "message": "Hi there!"}
    dummy_task.delay(dummy_task_json)
    print("Started celery task")
    return "<h1>Started celery task</h1>"
