FROM python:3.10.8-slim-buster as base

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get -y install git
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Deployment stage
FROM base as build

COPY ./model_manager ./model_manager

EXPOSE 9001

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY ./requirements.dev.txt ./requirements.dev.txt
RUN pip install -r requirements.dev.txt

COPY ./tests tests
RUN mkdir test-reports
RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode
