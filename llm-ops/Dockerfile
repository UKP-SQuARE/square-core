FROM nvidia/cuda:11.1.1-devel-ubuntu20.04

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

# create sym links for py
RUN ln -sf $(which ${PYTHON}) /usr/local/bin/python && \
    ln -sf $(which ${PYTHON}) /usr/local/bin/python3 && \
    ln -sf $(which ${PYTHON}) /usr/bin/python && \
    ln -sf $(which ${PYTHON}) /usr/bin/python3

WORKDIR /llm-ops

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./llm_ops ./llm_ops

COPY startup.sh ./start_chat.sh
RUN chmod 755 ./start_chat.sh

VOLUME [ "/deps" ]
VOLUME [ "/apps" ]
VOLUME [ "/root/.cache/huggingface" ]

EXPOSE 21002
