#!/bin/sh
source env/bin/activate
exec celery -A myapp.celery_utils.celery_app worker --loglevel=info
