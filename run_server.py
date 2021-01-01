import os
import subprocess
import sys

from workers import redis_pubsub_worker, rabbit_worker


def run_app():
    os.environ["FLASK_APP"] = "webapp"
    os.environ["FLASK_ENV"] = "development"
    os.environ["LOCAL_RUN"] = "yes"

    subprocess.call(["flask", "run"])


def run_redis():
    subprocess.call(["docker", "run", "--rm", "-d", "-p", "6379:6379", "redis"])


def run_rabbit():
    subprocess.call(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "-p",
            "5672:5672",
            "-p",
            "15672:15672",
            "rabbitmq:3-management",
        ]
    )


def run_celery():
    run_redis()
    run_rabbit()


def run_redis_worker():
    redis_pubsub_worker.run_worker()

def run_rabbit_worker():
    rabbit_worker.run_worker()


def run_celery_worker():
    subprocess.call(
        [
            "celery",
            "-A",
            "workers.celery_worker.celery_app",
            "worker",
            "--loglevel=info",
        ]
    )


if __name__ == "__main__":
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["RABBIT_HOST"] = "localhost"
    os.environ["RABBIT_USER"] = "guest"
    os.environ["RABBIT_PASSWORD"] = "guest"
    
    params = sys.argv[1:]
    if params:
        for param in params:
            if param == "redis":
                run_redis()
                run_redis_worker()
            elif param == "rabbit":
                run_rabbit()
                run_rabbit_worker()
            elif param == "celery":
                run_celery()
                run_celery_worker()
            elif param == "app":
                run_app()
            else:
                raise Exception(f"This is not valid param - {param}")
    else:
        run_app()
