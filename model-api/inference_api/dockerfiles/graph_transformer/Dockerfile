# Template dockerfile for graph_transformer
FROM ukpsquare/square-model-api-base-model:latest as base

ENV PYTHONUNBUFFERED=1

WORKDIR /inference_api

COPY ./dockerfiles/graph_transformer/requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install torch-scatter torch-sparse torch-geometric -f https://data.pyg.org/whl/torch-1.13.0+cpu.html

FROM base as test

RUN pip install pytest pytest-cov pytest-asyncio pytest-env
RUN mkdir test-reports

# copy application files
COPY ./app ./app
COPY main.py main.py
COPY logging.conf logging.conf
COPY ./tasks tasks

# copy test files
ENV MODEL transformer
COPY tests/pre_test_setup_for_docker_caching.py tests/pre_test_setup_for_docker_caching.py
COPY tests/$MODEL tests/$MODEL
COPY tests/generic/ tests/$MODEL/generic
COPY pytest.ini pytest.ini

# run tests
RUN python ./tests/pre_test_setup_for_docker_caching.py --transformer

RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode

# Deployment stage
FROM base as build

COPY main.py main.py
COPY ./app app
COPY logging.conf logging.conf

COPY ./tasks tasks

EXPOSE 8000
