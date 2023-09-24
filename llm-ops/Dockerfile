FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Update and install OS dependencies, and other necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
    ca-certificates \
    git \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install python
ARG PYTHON=python3.10
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    ${PYTHON} lib${PYTHON} python3-pip && \
    apt-get clean && \
    rm -rf  /var/lib/apt/lists/*

# install and upgrade pip
RUN pip --no-cache-dir install --upgrade \
    pip \
    setuptools

# create sym links for py
RUN ln -sf $(which ${PYTHON}) /usr/local/bin/python && \
    ln -sf $(which ${PYTHON}) /usr/local/bin/python3 && \
    ln -sf $(which ${PYTHON}) /usr/bin/python && \
    ln -sf $(which ${PYTHON}) /usr/bin/python3

WORKDIR /llm-ops

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./llm_ops ./llm_ops

COPY startup.sh ./start_fastchat.sh
RUN chmod 755 ./start_fastchat.sh

VOLUME [ "/deps" ]
VOLUME [ "/apps" ]
VOLUME [ "/root/.cache/huggingface" ]

EXPOSE 7860
EXPOSE 8000
ENV FS_ENABLE_WEB=true
ENV FS_ENABLE_OPENAI_API=true
ENV FS_ENABLE_HF_API=false

ENTRYPOINT [ "/bin/bash", "./start_fastchat.sh" ]
CMD ["--model-path lmsys/vicuna-7b-v1.3 --max-gpu-memory 14Gib"]