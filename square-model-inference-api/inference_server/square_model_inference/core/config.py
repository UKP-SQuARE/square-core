from starlette.config import Config

APP_VERSION = "0.1.0"
APP_NAME = "SQuARE Model Inference API"
API_PREFIX = "/api"

config = Config(".env")

# Disable CUDA even if available
DISABLE_GPU: bool = config("DISABLE_GPU", cast=bool, default=False)
# Corresponds to the Huggingface name for Transformers
MODEL_NAME: str = config("MODEL_NAME")
# Type of the model, e.g. Transformers, Adapter, ...
MODEL_TYPE: str = config("MODEL_TYPE")
# Cache directory where model weights are stored
TRANSFORMERS_CACHE: str = config("TRANSFORMERS_CACHE")

MAX_BATCH_SIZE: int = config("MAX_BATCH_SIZE", cast=int, default=32)

# For MODEL_TYPE=transformers: decides the AutoModelFor* class used
MODEL_CLASS: str = config("MODEL_CLASS", default="base")

# Flag that decides if returned numpy arrays are returned as lists or encoded to base64 (smaller but not easily human readable)
RETURN_PLAINTEXT_ARRAYS = config("RETURN_PLAINTEXT_ARRAYS", cast=bool, default=False)