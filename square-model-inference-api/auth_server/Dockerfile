FROM python:3.7.6-slim-buster

ENV PYTHONUNBUFFERED 1

EXPOSE 8081
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]