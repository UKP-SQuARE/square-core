#!/bin/bash

# Find the value for --model-path using sed
model_path=$(echo "$@" | awk -F'--model-path ' '{print $2}' | awk '{print $1}')

# Extract the model name after the "/" character
short_model_name=$(basename "$model_path")

# Print args
echo "Model path: $model_path"
echo "Model name: $short_model_name"
echo "Worker args: $@"
echo "Enable web: $FS_ENABLE_WEB"
echo "Enable OpenAI API: $FS_ENABLE_OPENAI_API"

# Start the model worker
python3 -m llm_ops.app.vllm_worker --host 0.0.0.0 \
                                    --port 21002 \
                                    --worker-address http://llm_worker:21002 \
                                    --controller-address http://llm_controller:21001 $@
