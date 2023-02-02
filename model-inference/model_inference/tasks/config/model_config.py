import json
import os
from collections.abc import Mapping
from dataclasses import asdict, dataclass

from model_inference.app.models.statistics import ModelStatistics
from filelock import FileLock
from starlette.config import Config


APP_VERSION = "0.1.0"
APP_NAME = "SQuARE Model Inference API"
API_PREFIX = "/api"
OPENAPI_URL = "/api/openapi.json"

CONFIG_PATH = os.getenv("CONFIG_PATH")
IDENTIFIER = os.getenv("QUEUE")


@dataclass
class ModelConfig(Mapping):
    # Corresponds to the Huggingface name for finetuned Transformers or the name of a finetuned SentenceTransformers
    model_name: str = None
    # Type of the model, e.g. Transformers, Adapter, ...
    # See square_model_inference.core.event_handlers.MODEL_MAPPING for all available names with corresponding model
    model_type: str = None

    is_encoder_decoder: bool = False

    # data paths to store additional data
    data_path: str = None

    preloaded_adapters: bool = True
    # Disable CUDA even if available
    disable_gpu: bool = False
    # Batch size used for many inputs
    batch_size: int = 32
    # Inputs larger than this size are rejected
    max_input_size: int = 1024

    # Cache directory where model weights are stored
    # This is the name for the env variable used by transformers and sentence-transformers package
    transformers_cache: str = None

    # For MODEL_TYPE=transformers: decides the AutoModel* class used
    # See square_model_inference.inference.transformer.CLASS_MAPPING for valid names and corresponding class
    model_class: str = "base"

    # Flag that decides if returned numpy arrays are returned
    # as lists or encoded to base64 (smaller but not easily human readable).
    # See the comment in square_model_inference.models.prediction._encode_numpy on information on how to decode
    # the base64 string back to the numpy array
    return_plaintext_arrays: bool = False

    # Flag that decides if quantized ONNX model should be used for inference
    onnx_use_quantized: bool = False

    # Flag that decides if ONNX model is encoder-decoder model
    is_encoder_decoder: bool = False

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def to_dict(self):
        return asdict(self)

    def to_statistics(self):
        return ModelStatistics(
            model_type=self.model_type,
            model_name=self.model_name,
            model_class=self.model_class,
            batch_size=self.batch_size,
            max_input=self.max_input_size,
            disable_gpu=self.disable_gpu,
            return_plaintext_arrays=self.return_plaintext_arrays,
            model_path=self.model_path,
            data_path=self.data_path,
            decoder_path=self.decoder_path,
            preloaded_adapters=self.preloaded_adapters,
            transformers_cache=self.transformers_cache,
        )

    def update(self, identifier: str=IDENTIFIER):
        with open(f"{CONFIG_PATH}/{identifier}.json", "r") as f:
            config = json.load(f)

        self.model_name = config["model_name"]
        self.model_type = config["model_type"]
        self.is_encoder_decoder = config["is_encoder_decoder"]
        self.data_path = config["data_path"]
        self.preloaded_adapters = config["preloaded_adapters"]
        self.disable_gpu = config["disable_gpu"]
        self.batch_size = config["batch_size"]
        self.max_input_size = config["max_input_size"]
        self.transformers_cache = config["transformers_cache"]
        self.model_class = config["model_class"]
        self.return_plaintext_arrays = config["return_plaintext_arrays"]

    @staticmethod
    def load(path=".env"):  # change .env filename to work on local
        config = Config(path)
        model_config = ModelConfig(
            model_name=config("MODEL_NAME", default=None),
            model_type=config("MODEL_TYPE", default=None),
            is_encoder_decoder=config("IS_ENCODER_DECODER", cast=bool, default=False),
            data_path=config("DATA_PATH", default=None),
            preloaded_adapters=config("PRELOADED_ADAPTERS", cast=bool, default=True),
            disable_gpu=config("DISABLE_GPU", cast=bool, default=False),
            batch_size=config("BATCH_SIZE", cast=int, default=32),
            max_input_size=config("MAX_INPUT_SIZE", cast=int, default=1024),
            transformers_cache=config("TRANSFORMERS_CACHE", default=None),
            model_class=config("MODEL_CLASS", default="base"),
            return_plaintext_arrays=config("RETURN_PLAINTEXT_ARRAYS", cast=bool, default=False),
            onnx_use_quantized=config("ONNX_USE_QUANTIZED", cast=bool, default=False),
        )
        model_config.save(IDENTIFIER)
        return model_config

    @staticmethod
    def load_from_file(identifier):
        identifier = identifier.replace("/", "-")
        with FileLock(f"{CONFIG_PATH}/{identifier}.lock"):
            with open(f"{CONFIG_PATH}/{identifier}.json", "r") as f:
                config = json.load(f)
        return ModelConfig(**config)

    def save(self, identifier):
        identifier = identifier.replace("/", "-")
        if not os.path.exists(f"{CONFIG_PATH}/{identifier}.json"):
            try:
                os.makedirs(os.path.dirname(f"{CONFIG_PATH}/{identifier}.json"))
            except OSError as err:
                print(err)
        with FileLock(f"{CONFIG_PATH}/{identifier}.lock"):
            with open(f"{CONFIG_PATH}/{identifier}.json", "w+") as json_file:
                json.dump(self.to_dict(), json_file)


model_config = ModelConfig.load()


# for testing the inference models
def set_test_config(
    model_name,
    disable_gpu,
    batch_size,
    model_type,
    max_input_size,
    model_class="base",
    cache="./.cache",
    preloaded_adapters=False,
    is_encoder_decoder=False,
    data_path="",
    onnx_use_quantized=False,
):
    global model_config
    model_config.model_name = model_name
    model_config.model_class = model_class
    model_config.disable_gpu = disable_gpu
    model_config.model_type = model_type
    model_config.batch_size = batch_size
    model_config.max_input_size = max_input_size
    model_config.transformers_cache = cache
    model_config.preloaded_adapters = preloaded_adapters
    model_config.data_path = data_path
    model_config.is_encoder_decoder = is_encoder_decoder
    model_config.onnx_use_quantized = onnx_use_quantized


if os.getenv("TEST", 0) == "1":
    TEST_MODEL_PATH = os.getenv("TEST_MODEL_PATH", "./model4test")
    set_test_config(TEST_MODEL_PATH, True, 8, "adapter", 512)
    model_config.save(IDENTIFIER)
