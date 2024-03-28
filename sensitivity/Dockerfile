FROM nvidia/cuda:11.1.1-runtime-ubuntu20.04 AS base

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Update and install OS dependencies, and other necessary packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  python3.9 \
  python3-pip \
  git \
  curl \
  ffmpeg \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create symlinks for Python
RUN ln -sf $(which python3.9) /usr/local/bin/python && \
    ln -sf $(which python3.9) /usr/local/bin/python3 && \
    ln -sf $(which python3.9) /usr/bin/python && \
    ln -sf $(which python3.9) /usr/bin/python3

WORKDIR /sensitivity

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Build stage
FROM base AS build

COPY ./app ./app

EXPOSE 8000

CMD ["python3", "-m", "app.sensitivity", "--port", "8000"]