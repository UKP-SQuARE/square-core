FROM python:3.10.8-slim-buster as base

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# required to install packages from github
RUN apt-get -y update && apt-get -y install build-essential 
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.base.txt
RUN pip install -r requirements.base.txt

RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader words


FROM base as build

ARG MODEL_TYPE
COPY requirements.$MODEL_TYPE.txt ./requirements.$MODEL_TYPE.txt 
RUN pip install -r requirements.${MODEL_TYPE}.txt 

COPY ./model_inference ./model_inference
COPY ./model_inference/tasks tasks
COPY logging.conf logging.conf

EXPOSE 8000


FROM build as test

ARG TEST_DIR

COPY ./requirements.dev.txt ./requirements.dev.txt
RUN pip install -r requirements.dev.txt
RUN mkdir test-reports

# copy test files
COPY tests/pre_test_setup_for_docker_caching.py tests/pre_test_setup_for_docker_caching.py
COPY tests/$TEST_DIR tests/$TEST_DIR
COPY tests/generic/ tests/$TEST_DIR/generic
COPY pytest.ini pytest.ini

# run tests
ARG TEST_SETUP
RUN python ./tests/pre_test_setup_for_docker_caching.py --$TEST_SETUP

RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode
