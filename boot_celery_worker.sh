#!/bin/sh
source env/bin/activate
exec celery -A workers.celery_worker.celery_app worker --loglevel=info
