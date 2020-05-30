#! /bin/sh
pipenv run python manage.py migrate
pipenv run gunicorn --bind :8000 sistemita.wsgi:application --daemon --workers 3
