from typing import Callable

from fastapi import FastAPI
from loguru import logger

from square_model_inference.inference.adaptertransformer import AdapterTransformer
from square_model_inference.core.config import MODEL_TYPE
from square_model_inference.inference.transformer import Transformer

MODEL_MAPPING = {
    "adapter": AdapterTransformer,
    "transformer": Transformer
}


def _startup_model(app: FastAPI) -> None:
    if MODEL_TYPE not in MODEL_MAPPING:
        raise RuntimeError(f"Unknown MODEL_MAPPING. Must be one of {MODEL_MAPPING.keys()}")
    model_instance = MODEL_MAPPING[MODEL_TYPE]()
    app.state.model = model_instance


def _shutdown_model(app: FastAPI) -> None:
    app.state.model = None


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_model(app)

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)

    return shutdown
