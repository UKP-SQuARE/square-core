# Template dockerfile for graph_transformer
FROM ukpsquare/square-model-api-base-model:latest as build

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install torch-scatter torch-sparse torch-geometric -f https://data.pyg.org/whl/torch-1.11.0+cpu.html
COPY ./dockerfiles/graph_transformer/requirements.txt ./requirements.graph.txt
RUN pip install -r requirements.graph.txt

FROM build as test

COPY ./requirements.dev.txt ./requirements.dev.txt
RUN pip install -r requirements.dev.txt
RUN mkdir test-reports

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
