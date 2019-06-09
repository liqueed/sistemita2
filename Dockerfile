FROM python:3.7.3-alpine3.9

ENV PYTHONUNBUFFERED 1
RUN pip install pipenv
RUN mkdir -p /app
WORKDIR /app
ADD Pipfile /app
ADD Pipfile.lock /app
RUN pipenv install --system --deploy --ignore-pipfile
COPY . /app
EXPOSE 8000

