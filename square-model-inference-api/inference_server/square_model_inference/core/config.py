from starlette.config import Config

APP_VERSION = "0.1.0"
APP_NAME = "SQuARE Model Inference API"
API_PREFIX = "/api"

config = Config(".env")

# Disable CUDA even if available
DISABLE_GPU: bool = config("DISABLE_GPU", cast=bool, default=False)
# Corresponds to the Huggingface name for finetuned Transformers or the name of a finetuned SentenceTransformers
MODEL_NAME: str = config("MODEL_NAME")
# Type of the model, e.g. Transformers, Adapter, ...
# See square_model_inference.core.event_handlers.MODEL_MAPPING for all available names with corresponding model
MODEL_TYPE: str = config("MODEL_TYPE")
# Cache directory where model weights are stored
# This is the name for the env variable used by transformers and sentence-transformers package
TRANSFORMERS_CACHE: str = config("TRANSFORMERS_CACHE")

# Batch size used for many inputs
BATCH_SIZE: int = config("BATCH_SIZE", cast=int, default=32)

# For MODEL_TYPE=transformers: decides the AutoModel* class used
# See square_model_inference.inference.transformer.CLASS_MAPPING for valid names and corresponding class
MODEL_CLASS: str = config("MODEL_CLASS", default="base")

# Flag that decides if returned numpy arrays are returned
# as lists or encoded to base64 (smaller but not easily human readable).
# See the comment in square_model_inference.models.prediction._encode_numpy on information on how to decode
# the base64 string back to the numpy array
RETURN_PLAINTEXT_ARRAYS = config("RETURN_PLAINTEXT_ARRAYS", cast=bool, default=False)
