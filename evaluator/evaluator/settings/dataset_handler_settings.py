from pydantic import BaseSettings, Field


class DatasetHandlerSettings(BaseSettings):
    dataset_dir: str = Field(..., env="DATASET_DIR")
