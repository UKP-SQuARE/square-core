FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y install git
RUN pip install --upgrade pip

# install rabbit mq backend
RUN apt-get install -y rabbitmq-server

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Deployment stage
FROM base as build

COPY main.py main.py
COPY models.py models.py
COPY docker_access.py docker_access.py
COPY logging.conf logging.conf
COPY ./tasks tasks

EXPOSE 8000
