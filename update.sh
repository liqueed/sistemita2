#! /bin/sh
git pull
docker-compose -f docker-compose.production.yml build
docker-compose stop
docker-compose -f docker-compose.production.yml up -d
docker-compose -f docker-compose.production.yml run app pipenv run ./manage.py migrate
