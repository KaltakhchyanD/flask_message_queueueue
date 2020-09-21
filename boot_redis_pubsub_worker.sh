#!/bin/sh
source env/bin/activate

exec python3 redis_pubsub_worker.py