FROM python:3.7.6-slim-buster as base

# required to install packages from github
RUN apt-get -y update --allow-insecure-repositories
RUN apt-get -y install git

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./skill_manager skill_manager

COPY logging.conf logging.conf

FROM base as test
RUN apt -y install docker.io

COPY requirements.dev.txt requirements.dev.txt 
RUN pip install -r requirements.dev.txt

COPY tests tests
ENV INSIDE_DOCKER 0
# RUN python -m pytest
CMD ["python", "-m", "pytest"]

FROM base as build
EXPOSE 8008

CMD ["uvicorn", "skill_manager.api:app", "--host", "0.0.0.0", "--port", "8008", "--log-config", "logging.conf"]
