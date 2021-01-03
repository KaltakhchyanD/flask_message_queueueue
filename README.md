# flask_message_queueueue
Dummy Flask app to check queues with Redis, RabbitMQ and Celery

This app requires python3.6 and Docker

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
