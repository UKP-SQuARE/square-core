FROM python:3.10.8-slim-buster as build

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get -y update && apt-get -y install git

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
ARG skill
COPY ./$skill/. .
COPY ./$skill/requirements.txt* .
RUN if [ -f "./requirements.txt" ] ; then pip install -r requirements.txt ; fi

COPY main.py main.py
COPY utils.py utils.py
COPY logging.conf logging.conf

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "logging.conf"]
