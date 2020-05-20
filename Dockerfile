FROM python:3.7-buster

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales
RUN sed -i -e 's/# es_AR ISO-8859-1/es_AR ISO-8859-1/' /etc/locale.gen
RUN locale-gen 
RUN apt-get install -y graphviz
RUN apt-get update
RUN apt-get install -y firefox-esr
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz -P /opt/
RUN tar -xvzf /opt/geckodriver* -C /opt/
RUN chmod +x /opt/geckodriver
ENV PATH="/opt/:${PATH}"
ENV PYTHONUNBUFFERED 1
RUN pip install pipenv
RUN mkdir -p /app
WORKDIR /app
ADD Pipfile /app
ADD Pipfile.lock /app
#RUN pipenv install --deploy --system
RUN pipenv install
COPY . /app
EXPOSE 8000
