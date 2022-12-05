## This is the dockerfile template for transformer based model
FROM ukpsquare/model-inference-base-model:latest as base

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ./dockerfiles/transformer/requirements.txt ./requirements.transformer.txt
RUN pip install -r requirements.transformer.txt

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY ./requirements.dev.txt ./requirements.dev.txt
RUN pip install -r requirements.dev.txt
RUN mkdir test-reports
RUN ls
RUN pwd

# copy test files
COPY tests/pre_test_setup_for_docker_caching.py tests/pre_test_setup_for_docker_caching.py
COPY tests/transformer tests/transformer
COPY tests/generic/ tests/transformer/generic
COPY pytest.ini pytest.ini

# run tests
RUN python ./tests/pre_test_setup_for_docker_caching.py --transformer

RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode
