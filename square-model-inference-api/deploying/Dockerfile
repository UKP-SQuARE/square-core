FROM python:3.7.6-slim-buster as base

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Deployment stage
FROM base as build

COPY main.py main.py
COPY models.py models.py
COPY docker_access.py docker_access.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]