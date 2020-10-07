import os

from celery import Celery


def make_celery(app_name=__name__):
    user = os.getenv('RABBIT_USER')
    password = os.getenv('RABBIT_PASSWORD')
    host = os.getenv('RABBIT_HOST')

    celery_app = Celery(app_name, broker=f"pyamqp://{user}:{password}@{host}:5672")
    # celery.conf.update(app.config)
    return celery_app


def init_celery(celery_app, app):
    celery_app.conf.update(app.config)
    TaskBase = celery_app.Task

    class ContextTask(TaskBase):
        testcheck = "CtxTask"

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask