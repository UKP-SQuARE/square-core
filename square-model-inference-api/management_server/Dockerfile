FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y install git
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Deployment stage
FROM base as build

COPY ./app app
COPY main.py main.py
COPY docker_access.py docker_access.py
COPY logging.conf logging.conf
COPY ./tasks tasks
#COPY ./mongo_access.py mongo_access.py

EXPOSE 9001

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY ./tests tests
COPY . ./
RUN pip install pytest pytest-cov pytest-asyncio
RUN mkdir test-reports
RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode
