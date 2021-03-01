#!/bin/bash
django-admin collectstatic --noinput
gunicorn --bind :8000 --workers "$GUNICORN_WORKERS" foxtail.wsgi:application
