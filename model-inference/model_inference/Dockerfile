FROM python:3.9.14-slim-buster as base

ENV PYTHONUNBUFFERED 1

# required to install packages from github
RUN apt-get -y update && apt-get -y install git rabbitmq-server

RUN pip install --upgrade pip

WORKDIR /app

RUN pip install nltk
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader words

COPY requirements1.txt ./
RUN pip install -r requirements1.txt

COPY uninstall_requirements.txt ./
RUN pip uninstall -y -r uninstall_requirements.txt

COPY requirements2.txt ./
RUN pip install -r requirements2.txt

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY tests/pre_test_setup_for_docker_caching.py ./tests/pre_test_setup_for_docker_caching.py
RUN python ./tests/pre_test_setup_for_docker_caching.py
COPY inference_server ./
RUN pip install pytest pytest-cov pytest-asyncio pytest-env
RUN mkdir test-reports
RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode

# Deployment stage
FROM base as build

COPY main.py main.py
COPY ../app square_model_inference
COPY ../logging.conf logging.conf

COPY tasks tasks

EXPOSE 8000
