FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y install git
RUN pip install --upgrade pip

WORKDIR ./explainability-api

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./app app
COPY ./tasks tasks
COPY main.py main.py
COPY logging.conf logging.conf

EXPOSE 8010
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]