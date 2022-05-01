FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y install git
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./app app
ENV PYTHONPATH=/app

COPY ./tasks tasks
COPY main.py main.py
COPY logging.conf logging.conf

COPY worker-start.sh worker-start.sh

RUN chmod +x worker-start.sh

CMD ["bash", "worker-start.sh"]
