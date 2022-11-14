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

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

RUN pip install pytest pytest-cov pytest-asyncio pytest-env
RUN mkdir test-reports

# copy application files
COPY ./app ./app
COPY main.py main.py
COPY logging.conf logging.conf
COPY ./tasks tasks

# copy test files
COPY tests/pre_test_setup_for_docker_caching.py tests/pre_test_setup_for_docker_caching.py
COPY tests/generic/ tests/generic
COPY pytest.ini pytest.ini

## run tests
#RUN python ./tests/pre_test_setup_for_docker_caching.py --transformer
#
RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode

# Deployment stage
FROM base as build

COPY ./app ./app
COPY main.py main.py
COPY logging.conf logging.conf
COPY ./tasks tasks

EXPOSE 8000
