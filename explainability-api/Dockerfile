FROM python:3.7.6-slim-buster as base

WORKDIR /explainability_api

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
