#!/bin/bash
django-admin collectstatic --noinput
gunicorn --bind :8000 --workers 4 foxtail.wsgi:application
