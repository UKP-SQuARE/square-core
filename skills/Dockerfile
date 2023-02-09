FROM python:3.10.8-slim-buster as build

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get -y update && apt-get -y install git

WORKDIR /app

RUN pip install --upgrade pip
COPY square-core/skills/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY square-skill-api square-skill-api
RUN pip install --editable square-skill-api

COPY square-core/skills/main.py main.py
COPY square-core/skills/utils.py utils.py

COPY square-core/skills/extractive-qa/skill.py skill.py 
COPY square-core/skills/logging.conf logging.conf

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "logging.conf"]
