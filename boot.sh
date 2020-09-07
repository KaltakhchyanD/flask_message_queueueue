#!/bin/sh
source env/bin/activate

exec gunicorn webapp:app -b :5555 -w 5