#FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04
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

COPY startup.sh ./start_fastchat.sh
RUN chmod 755 ./start_fastchat.sh

VOLUME [ "/deps" ]
VOLUME [ "/apps" ]
VOLUME [ "/root/.cache/huggingface" ]

EXPOSE 7860
#EXPOSE 8000
ENV FS_ENABLE_WEB=true
#ENV FS_ENABLE_OPENAI_API=true
ENV FS_ENABLE_HF_API=false

ENTRYPOINT [ "/bin/bash", "./start_fastchat.sh" ]
CMD ["--model-path lmsys/vicuna-7b-v1.3 --max-gpu-memory 14Gib"]

#FROM nvidia/cuda:11.1.1-runtime-ubuntu20.04
#
#ARG DEBIAN_FRONTEND=noninteractive
#
#ENV PYTHONUNBUFFERED=1
#
#RUN apt-get update -y && apt-get install -y python3.9 python3.9-distutils curl
#RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#RUN python3.9 get-pip.py
#RUN pip3 install fschat[model_worker,webui] pydantic==1.10.1
#RUN pip3 install --force-reinstall typing-extensions==4.5.0
