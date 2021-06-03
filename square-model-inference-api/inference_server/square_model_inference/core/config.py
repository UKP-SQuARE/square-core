from starlette.config import Config

APP_VERSION = "0.1.0"
APP_NAME = "SQuARE Model Inference API"
API_PREFIX = "/api"

config = Config(".env")

IS_DEBUG: bool = config("IS_DEBUG", cast=bool, default=False)

DISABLE_GPU: bool = config("DISABLE_GPU", cast=bool, default=False)
MODEL_NAME: str = config("MODEL_NAME")
MODEL_TYPE: str = config("MODEL_TYPE")
TRANSFORMERS_CACHE: str = config("TRANSFORMERS_CACHE")

MAX_BATCH_SIZE: int = config("MAX_BATCH_SIZE", cast=int, default=32)

RETURN_PLAINTEXT_ARRAYS = config("RETURN_PLAINTEXT_ARRAYS", cast=bool, default=False)