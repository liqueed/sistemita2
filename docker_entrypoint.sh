#! /bin/bash
pipenv run python sistemita/manage.py migrate
pipenv run python sistemita/manage.py runserver 0.0.0.0:8000
