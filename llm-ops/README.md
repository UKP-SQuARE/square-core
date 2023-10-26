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

4. Mistral 7B
```python
mistralai/Mistral-7B-v0.1
mistralai/Mistral-7B-Instruct-v0.1
```
5. Falcon
```python
tiiuae/falcon-7b
tiiuae/falcon-7b-instruct
tiiuae/falcon-40b
tiiuae/falcon-40b-instruct
tiiuae/falcon-180B
tiiuae/falcon-180B-chat
```

### Usage

1. Using docker 
```python

# build application
cd llm-ops
make build

# shutdown application
make clean
```

Once the applications are up and running, you can use the apis listed in the file `api.http`
