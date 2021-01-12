import os

from celery import Celery

class CeleryClient():

    def __init__(self):
        self.connection = None

    def make_celery(self, app_name=__name__):
        user = os.getenv("RABBIT_USER")
        password = os.getenv("RABBIT_PASSWORD")
        host = os.getenv("RABBIT_HOST")
        redis_host = os.getenv("REDIS_HOST")
        backend = f"redis://{redis_host}"

        celery_app = Celery(
            app_name, backend=backend, broker=f"pyamqp://{user}:{password}@{host}:5672"
        )
        # celery.conf.update(app.config)
        return celery_app


    def init_celery(self, celery_app, app):
        celery_app.conf.update(app.config)
        TaskBase = celery_app.Task

        class ContextTask(TaskBase):
            testcheck = "CtxTask"

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery_app.Task = ContextTask
