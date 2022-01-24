FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

# required to install packages from github
RUN apt-get -y update
RUN apt-get -y install git

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py main.py
COPY ./skillapi skillapi
COPY logging.conf logging.conf

# Deployment stage
FROM base as build

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--log-config", "logging.conf"]
