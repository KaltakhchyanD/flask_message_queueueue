from celery import Celery


def make_celery(app_name=__name__):
    celery_app = Celery(app_name, broker="pyamqp://rabbit:mq@rabbit:5672")
    #celery_app = Celery(app_name, broker="pyamqp://guest:guest@localhost:5672")
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


celery_app = make_celery("myapp")
