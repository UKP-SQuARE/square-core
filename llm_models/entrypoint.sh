#!/bin/bash

# Set your username and password from environment variables
HF_USERNAME="$HF_USERNAME"
HF_PASSWORD="$HF_PASSWORD"

# Check if the Hugging Face model repository exists
if [ ! -d "/app/data/Llama-2-7b-chat-hf" ]; then
    if ! command -v git &> /dev/null; then
        echo "Git not found. Installing Git..."
        apt-get update
        apt-get install -y git
        apt-get install git-lfs
        git lfs install
    fi

    echo "Cloning Hugging Face model repository..."
    git clone "https://$HF_USERNAME:$HF_PASSWORD@huggingface.co/meta-llama/Llama-2-7b-chat-hf" /app/data/Llama-2-7b-chat-hf
else
    echo "Hugging Face model repository already exists. Skipping cloning."
fi

# Run the FastAPI app using uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000