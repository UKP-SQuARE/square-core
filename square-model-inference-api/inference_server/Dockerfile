FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

COPY ElkJsonFormatter.tar.gz ./ElkJsonFormatter.tar.gz
RUN pip install --upgrade pip
COPY requirements1.txt requirements2.txt uninstall_requirements.txt ./
RUN pip install -r requirements1.txt
RUN pip uninstall -y -r uninstall_requirements.txt
RUN pip install -r requirements2.txt

# Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
# run the tests
FROM base as test

COPY ./tests/pre_test_setup_for_docker_caching.py ./tests/pre_test_setup_for_docker_caching.py
RUN python ./tests/pre_test_setup_for_docker_caching.py
COPY . ./
RUN pip install pytest pytest-cov pytest-asyncio
RUN mkdir test-reports
RUN PYTHONPATH=./ pytest \
    --ignore ./test/test_onnx.py \
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

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.conf"]