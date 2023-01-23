# Corresponds to the Huggingface name for finetuned Transformers or the name of a finetuned SentenceTransformers
MODEL_NAME=facebook/dpr-question_encoder-single-nq-base
# Type of the model, e.g. Transformers, Adapter, ...
# See square_model_inference.core.event_handlers.MODEL_MAPPING for all available names with corresponding model
MODEL_TYPE=transformer

# Disable CUDA even if available
DISABLE_GPU=False
# Batch size used for many inputs
BATCH_SIZE=32
# Inputs larger than this size are rejected
MAX_INPUT_SIZE=1024

# Cache directory where model weights are stored
# This is the name for the env variable used by transformers and sentence-transformers package
TRANSFORMERS_CACHE=/etc/huggingface/.cache/

# For MODEL_TYPE=transformers: decides the AutoModel* class used
# See square_model_inference.inference.transformer.CLASS_MAPPING for valid names and corresponding class
MODEL_CLASS=base

# Flag that decides if returned numpy arrays are returned
# as lists or encoded to base64 (smaller but not easily human readable).
# See the comment in square_model_inference.models.prediction._encode_numpy on information on how to decode
# the base64 string back to the numpy array
RETURN_PLAINTEXT_ARRAYS=False
