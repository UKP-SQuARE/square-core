from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

API_KEY: Secret = config("API_KEY", cast=Secret)
API_KEY_NAME: str = config("API_KEY_NAME", cast=str, default="api_key")
