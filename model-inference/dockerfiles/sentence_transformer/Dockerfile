## This is the dockerfile template for sentence-transformer based model
FROM ukpsquare/square-model-api-base-model:latest as build

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MODEL sentence_transformer

WORKDIR /app

COPY ./dockerfiles/sentence_transformer/requirements.txt ./requirements.sentence_transformer.txt
RUN pip install -r requirements.sentence_transformer.txt

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY ./requirements.dev.txt ./requirements.dev.txt
RUN pip install -r requirements.dev.txt
RUN mkdir test-reports

# copy test files
COPY tests/pre_test_setup_for_docker_caching.py tests/pre_test_setup_for_docker_caching.py
COPY tests/sentence_transformer tests/sentence_transformer
COPY tests/generic/ tests/sentence_transformer/generic
COPY pytest.ini pytest.ini

RUN python ./tests/pre_test_setup_for_docker_caching.py --sentence_transformer

RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode
