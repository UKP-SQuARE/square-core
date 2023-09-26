FROM nvidia/cuda:11.1.1-devel-ubuntu20.04

ARG FASTCHAT_VERSION="main"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update ; \
    apt-get upgrade -y ; \
    apt-get install -y git python3-dev python3-pip

RUN pip3 install --upgrade pip


RUN git clone -b "$FASTCHAT_VERSION" --depth 1 https://github.com/lm-sys/FastChat fastchat

WORKDIR /fastchat
RUN pip3 install .
RUN pip3 install fschat[model_worker,webui] pydantic==1.10.1

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
