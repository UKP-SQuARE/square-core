FROM python:3.11-slim-buster as base

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# required to install packages from github
RUN apt-get -y update && apt-get -y install git

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./app ./app

# -- Test stage --
FROM base as test

RUN apt-get -y update && apt -y install docker.io

COPY ./requirements.dev.txt requirements.dev.txt
RUN pip install -r requirements.dev.txt

COPY ./tests ./tests
COPY ./.env.test ./.env
COPY ./pytest.ini ./pytest.ini
# RUN mkdir test-reports
# RUN PYTHONPATH="." MOCK_DEPENDENCIES=1 pytest \
#     --junitxml=test-reports/junit.xml \
#     --cov \
#     --cov-report=xml:test-reports/coverage.xml \
#     --cov-report=html:test-reports/coverage.html \
#     ./tests; \
#     echo $? > test-reports/pytest.exitcode

# -- Deploy stage --
FROM base as build

COPY logging.conf logging.conf

EXPOSE 7000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7000", "--log-config", "logging.conf"]
