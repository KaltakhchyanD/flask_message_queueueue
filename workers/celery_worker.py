import datetime
import random
import time

from flask import current_app, _app_ctx_stack

from workers.celery_utils import CeleryClient

celery_client = CeleryClient()
celery_app = celery_client.make_celery("myapp")

@celery_app.task
def add(a, b):
    return a + b


@celery_app.task
def write_task(something):
    if something == "to prinTTT":
        with open("temp.txt", "a") as file:
            file.write(f"{datetime.datetime.now()} \n")
    print(f"FROM TASK - {something}")
    return something


@celery_app.task
def dummy_task(task_json):
    task_id = task_json["task_id"]
    message = task_json["message"]
    random_delay = random.randint(10, 20)
    print(f" [x] Celery worker: Delaing for {random_delay} sec")
    time.sleep(random_delay)
    print(f" [x] Celery worker: Task for message {message} complete!")

    result_message = message+ "".join([str(random.randint(0, 9)) for i in range(3)])
    return result_message

