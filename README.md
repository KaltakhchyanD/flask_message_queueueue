# flask_message_queueueue
Dummy Flask app that uses queues with Redis, RabbitMQ and Celery

It has:
- /redis page, where you can "start task" and recieve result message via redis PubSub
- /rabbit page, where you can "start task" at 1 of 3 queues and recieve result
- /celery page, where you can "start task" with async celery worker and rabbit queue and recieve result message through result backend, which is redis

This app requires python3.6, docker, docker-compose

Installation:
- python3.6 -m venv env 
- source env/bin/activate
- git clone git@github.com:KaltakhchyanD/flask_message_queueueue.git flask_queue_app

Using without docker-compose
- cd flask_queue_app && python run_server.py
- in another terminal window - python run_server.py redis/rabbit/celery - this runs respective docker image with redis, rabbit or celery


Using with docker-compose
- docker compose build
- docker compose up
