import datetime

from flask import current_app, _app_ctx_stack


# app = Celery('celery_worker', broker = 'pyamqp://rabbit:mq@rabbit:5672')
#app = Celery("celery_worker", broker="pyamqp://guest:guest@localhost:5672")


# app.autodiscover_tasks()

from myapp.celery_utils import celery_app

@celery_app.task
def add(a, b):
    return a + b


@celery_app.task
def write_task(something):
    if something == "to prinTTT":
        with open("temp.txt", "a") as file:
            file.write(f"{datetime.datetime.now()} \n")
    print(f"FROM TASK - {something}")
    #print(f"App context - {_app_ctx_stack.top}")
    #print(f"Type of task - {type(celery_app.Task())}")
    #print(f"Attr cehck - {celery_app.Task.testcheck}")
    return something
