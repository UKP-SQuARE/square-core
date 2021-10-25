from starlette.config import Config

APP_VERSION = "0.1.0"
APP_NAME = "SQuARE Model Skill"
API_PREFIX = ""

config = Config(".env")

MODEL_API_KEY = config.get("MODEL_API_KEY")

MODEL_API_URL = config.get("MODEL_API_URL")
DATA_API_URL = config.get("DATA_API_URL")
