FROM python:3.7.6-slim-buster as base

# required to install packages from github
RUN apt-get -y update
RUN apt-get -y install git

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./skill_manager skill_manager

COPY logging.conf logging.conf

EXPOSE 8008

CMD ["uvicorn", "skill_manager.api:app", "--host", "0.0.0.0", "--port", "8008", "--log-config", "logging.conf"]
