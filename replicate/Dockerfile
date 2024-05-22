FROM python:3.12.3-slim AS base

# used to avoid interactive prompts during build
ARG DEBIAN_FRONTEND=noninteractive

# used to avoid buffering output from python
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install --no-install-recommends -y
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

FROM base AS build

COPY /app /app

CMD ["python3", "app.py", "--port", "8000"]

EXPOSE 8000
