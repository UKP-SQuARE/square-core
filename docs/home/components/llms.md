---
sidebar_position: 5
---

# LLM Ops

LLM Ops is a deployment service for LLMs that facilitates the deployment of LLMs on GPUs. It provides an API designed to support both chat and completion requests, accommodating streaming and non-streaming requests alike. The foundation of the service rests on the [FastChat](https://github.com/lm-sys/FastChat) platform. For model deployment on GPUs, LLM Ops utilizes the [vllm](https://github.com/vllm-project/vllm) serving engine.

## Model Deployment

### Requirements
- Docker

### Setup


The service is dockerized, enabling straightforward deployment through a single Docker command. To start the service, navigate to the `llm-ops` directory and run:

```bash
docker-compose up -d
```

### Deploying a Model
Currently, deploying a new model requires the model to be explicitly included in the docker-compose file. Below is a demonstration of deploying the LLaMA-2 7b chat model as an illustrative example.

```yaml
llm_chat:
    build:
      context: .
    container_name: llm_chat
    volumes:
      - /home/hf_models:/root/.cache/huggingface  # replace "/home/hf_models" with your own huggingface models directory
    deploy:
      resources:
        reservations:
          devices:  # adjust this based on the specification of your machine
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    entrypoint:
      - /bin/bash
      - ./start_chat.sh
    command:
      - --model-path
      - ../root/.cache/huggingface/Llama-2-7b-chat  # falcon-7b-instruct  # Llama-2-7b-chat # vicuna-7b-v1.3
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.llm-chat.rule=PathPrefix(`/api/Llama-2-7b-chat`)"  # API path of you model. Adjust it base on the model you deploy
      - "traefik.http.routers.llm-chat.entrypoints=websecure"
      - "traefik.http.routers.llm-chat.tls=true"
      - "traefik.http.routers.llm-chat.tls.certresolver=le"
      - "traefik.http.routers.llm-chat.middlewares=llm-chat-stripprefix,llm-chat-addprefix"
      - "traefik.http.middlewares.llm-chat-stripprefix.stripPrefixRegex.regex=/api/[a-zA-Z0-9_-]+"
      - "traefik.http.middlewares.llm-chat-addprefix.addPrefix.prefix=/api"
```

### Supported Models
Currently, the following models are supported by default: 
- LLama2
- Vicuna v1.1
- Dolly V2
- Falcon 180B
- Falcon
- Mistral-instruct-v0.1

If you want to add support to a new model, you have to consider the following: 
- The model has to be supported by [vllm](https://github.com/vllm-project/vllm). See: [Supported Models — vLLM](https://docs.vllm.ai/en/latest/models/supported_models.html)
- If you want to support a chat model, you also have to add a new `conv_template` in `llm-ops/llm_ops/prompts/conversation.py`. For example, here is how to add the conv_template for the LLama2 chat model: 

```python
register_conv_template(
    Conversation(
        name="llama-2",
        system_template="[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n",
        roles=("[INST]", "[/INST]"),
        sep_style=SeparatorStyle.LLAMA2,
        sep=" ",
        sep2=" </s><s>",
    )
)
```


## API
After starting the service with your model being deployed, you can make non-streaming or streaming requests. The following are examples of how to make requests to the deployed model Llama-2-7b-chat.

### Non-Streaming Request
```bash
curl -k -X POST https://localhost:8443/api/Llama-2-7b-chat/worker_generate \
-H "Content-Type: application/json" \
-d '{
    "model_identifier": "Llama-2-7b-chat",
    "messages": [
        {
            "role": "user",
            "text": "Hellow!"
        }, 
        {
            "role": "ai",
            "text": "Hey! How can I help you today?"
        },
        {
            "role": "user",
            "text": "Tell me a short funny joke."
        }
    ],
    "system_message": "The following is a friendly conversation between a human and an AI.",
    "temperature": 0.7,
    "top_p": 0.9,
    "echo": false,
    "generation_mode": "chat"
}'
```
`generation_mode` can be either `chat` or `completion` depending on the type of request you want to make. If you want to make a completion request, you have to set `generation_mode` to `completion` and provide a string `prompt` instead of `messages`.


### Streaming Request
The streaming request is very similar to the non-streaming request, but you have to use the endpoint `/api/Llama-2-7b-chat/worker_generate_stream` instead of `/api/Llama-2-7b-chat/worker_generate`. I replace the `messages` field with a `prompt` field just to show how to make a completion request too.
```bash
curl -k -X POST https://localhost:8443/api/Llama-2-7b-chat/worker_generate_stream \
-H "Content-Type: application/json" \
-d '{
    "model_identifier": "Llama-2-7b-chat",
    "prompt": "Hellow! Can you tell me a joke?",
    "system_message": "The following is a friendly conversation between a human and an AI.",
    "temperature": 0.7,
    "top_p": 0.9,
    "echo": false,
    "generation_mode": "completion"
}'
```

Note that in both non-streaming and streaming requests, you have to provide the `model_identifier`, `prompt` or `messages` and `generation_mode`. The other fields are optional. The `echo` field is used to determine whether the service should return the initial prompt/messages or not.