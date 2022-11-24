## This is the dockerfile template for base-model
FROM python:3.10.8-slim-buster as base

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# required to install packages from github
RUN apt-get -y update && apt-get -y install git rabbitmq-server

RUN pip install --upgrade pip

WORKDIR /app

COPY ./dockerfiles/base_model/requirements.txt ./requirements.base.txt
RUN pip install -r requirements.base.txt

RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader words

# Deployment stage
FROM base as build

COPY ./model_inference ./model_inference
COPY logging.conf logging.conf

EXPOSE 8000
