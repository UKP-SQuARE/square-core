FROM python:3.7.6-slim-buster as base

EXPOSE 8000
WORKDIR /app

RUN pip install --upgrade pip

COPY ./ElkJsonFormatter.tar.gz ./ElkJsonFormatter.tar.gz
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./app ./app
COPY ./scripts .

# -- Test stage --
FROM base as test

RUN pip install pytest pytest-cov
COPY ./tests ./tests
RUN mkdir test-reports
RUN PYTHONPATH="." pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode

# -- Deploy stage --
FROM base as build

COPY logging.conf logging.conf

CMD ["python" "run.py", "wait-vespa", "config"]
CMD ["python" "run.py", "wait-vespa", "app"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.conf"]
