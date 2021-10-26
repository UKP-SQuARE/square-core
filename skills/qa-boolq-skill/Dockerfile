FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

EXPOSE 8003
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
COPY ElkJsonFormatter.tar.gz ./
RUN pip install -r requirements.txt

COPY main.py main.py
COPY ./skillapi skillapi
COPY logging.conf logging.conf

FROM base as test
RUN pip install pytest pytest-cov pytest-asyncio pytest-mock
COPY ./tests tests
RUN mkdir test-reports
RUN PYTHONPATH=./ pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode

# Deployment stage
FROM base as build

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--log-config", "logging.conf"]
