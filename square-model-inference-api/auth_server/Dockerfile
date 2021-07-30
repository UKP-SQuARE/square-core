FROM python:3.7.6-slim-buster

ENV PYTHONUNBUFFERED 1

EXPOSE 8081
WORKDIR /app

COPY ElkJsonFormatter.tar.gz ./ElkJsonFormatter.tar.gz
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py main.py
COPY ./auth_api auth_api
COPY logging.conf logging.conf

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--log-config", "logging.conf"]