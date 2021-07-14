from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

# The API key required to get authorization
API_KEY: Secret = config("API_KEY", cast=Secret)
# Name of the header in the request that contains the API key
API_KEY_HEADER_NAME: str = config("API_KEY_HEADER_NAME", cast=str, default="Authorization")
