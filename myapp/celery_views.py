from flask import Blueprint, render_template, request, current_app

from workers.celery_worker import write_task

blueprint = Blueprint("celery", __name__, url_prefix="")


@blueprint.route("/celery")
def celery_view():
    write_task.delay("to prinTTT")
    return "Hey celery", 200
