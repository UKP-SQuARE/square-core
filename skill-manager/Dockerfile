FROM python:3.10.8-slim-buster as base

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# required to install packages from github
RUN apt-get -y update && apt-get -y install git

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# COPY ./square-model-client /square-model-client
# RUN pip install -e /square-model-client

COPY ./skill_manager skill_manager

COPY logging.conf logging.conf

FROM base as test
RUN apt update && apt -y install docker.io

COPY requirements.dev.txt requirements.dev.txt 
RUN pip install -r requirements.dev.txt

COPY tests tests
COPY pytest.ini pytest.ini

FROM base as build
EXPOSE 8000

CMD ["uvicorn", "skill_manager.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.conf"]
