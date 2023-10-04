## LLM Inference
Module for using LLMs for chat and normal inference.

### Supported Models
1. LLaMA-2 
```python
meta-llama/Llama-2-7b-chat-hf
meta-llama/Llama-2-7b-hf
```
2. Vicuna
```python
lmsys/vicuna-7b-v1.3
```
3. Dolly v2
```python
databricks/dolly-v2-7b
databricks/dolly-v2-12b
```


### Usage

1. For direct chat via terminal
```python
python3 -m llm_ops.app.chat_cli --model-path meta-llama/Llama-2-7b-chat-hf
```


2. Using docker 
```python
cd llm-ops
docker compose up -d --build

# to check docker logs
docker compose logs -f llm_chat

# shutdown application
docker compose down
```

If the container starts successfully, the application should be running
on http://localhost:7860
