FROM python:3.7.6-slim-buster as base

RUN pip install --upgrade pip

WORKDIR /app

RUN pip install --upgrade pip

COPY ElkJsonFormatter.tar.gz ./ElkJsonFormatter.tar.gz
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# not in requirements because we use SQLite for dev server
RUN pip install psycopg2-binary

COPY ./docker .
COPY flask-manage.py flask-manage.py
COPY main.py main.py
COPY ./squareapi squareapi

WORKDIR /app
RUN mkdir -p logs

FROM base as test
WORKDIR /app
RUN pip install pytest pytest-cov
COPY ./tests tests
RUN mkdir test-reports
RUN pytest \
    --junitxml=test-reports/junit.xml \
    --cov \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-report=html:test-reports/coverage.html; \
    echo $? > test-reports/pytest.existcode

FROM base as build

COPY logging.conf logging.conf

RUN ["chmod", "+x", "./entry.sh"]
ENTRYPOINT ["./entry.sh"]
