FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

# required to install packages from github
RUN apt-get -y update && apt-get -y install git rabbitmq-server

RUN pip install --upgrade pip

WORKDIR /app

COPY ./dockerfiles/graph_transformer/requirements1.txt ./
RUN pip install -r requirements1.txt
RUN pip install torch-scatter torch-sparse torch-geometric -f https://data.pyg.org/whl/torch-1.11.0+cpu.html

RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader words

COPY ./dockerfiles/graph_transformer/uninstall_requirements.txt ./
RUN pip uninstall -y -r uninstall_requirements.txt

COPY ./dockerfiles/graph_transformer/requirements2.txt ./
RUN pip install -r requirements2.txt

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY ./tests/pre_test_setup_for_docker_caching.py ./tests/pre_test_setup_for_docker_caching.py
RUN python ./tests/pre_test_setup_for_docker_caching.py --transformer
COPY . ./
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
COPY ./square_model_inference square_model_inference
COPY logging.conf logging.conf

COPY ./tasks tasks

EXPOSE 8000
