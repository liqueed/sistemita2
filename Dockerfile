FROM python:3.7-buster


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales
RUN sed -i -e 's/# es_AR ISO-8859-1/es_AR ISO-8859-1/' /etc/locale.gen
RUN locale-gen 
RUN apt-get install -y graphviz
ENV PYTHONUNBUFFERED 1
RUN pip install pipenv
RUN mkdir -p /app
WORKDIR /app
ADD Pipfile /app
ADD Pipfile.lock /app
RUN pipenv sync
COPY . /app
EXPOSE 8000

