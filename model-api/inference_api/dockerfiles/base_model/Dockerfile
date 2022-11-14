## This is the dockerfile template for base-model
FROM python:3.9.14-slim-buster as base

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MODEL base_model

# required to install packages from github
RUN apt-get -y update && apt-get -y install git rabbitmq-server

RUN pip install --upgrade pip

WORKDIR /inference_api

COPY ./dockerfiles/$MODEL/requirements.txt ./
RUN pip install -r requirements.txt

RUN pip install nltk
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader words

# Deployment stage
FROM base as build

COPY ./app ./app
COPY main.py main.py
COPY logging.conf logging.conf
COPY ./tasks tasks

EXPOSE 8000
