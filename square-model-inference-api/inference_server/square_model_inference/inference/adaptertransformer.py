import json

import torch
from loguru import logger

from transformers import AutoModelWithHeads
from transformers.adapters.utils import download_cached, ADAPTER_HUB_INDEX_FILE

from square_model_inference.inference.transformer import Transformer
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput


class AdapterTransformer(Transformer):
    def __init__(self, model_name, max_batch_size, disable_gpu, transformers_cache, **kwargs):
        self._load_model(AutoModelWithHeads, model_name, disable_gpu)
        self._load_adapter(model_name, transformers_cache)
        self.max_batch_size = max_batch_size

    def _load_adapter(self, model_name, transformers_cache):
        """
        Pre-load all available adapters for MODEL_NAME from adapterhub.ml.
        We parse the hub index to extract all names and then load each model.
        """
        logger.info("Loading all available adapters from adapterhub.ml")
        index_file = download_cached(ADAPTER_HUB_INDEX_FILE.format(model_name))
        adapter_index = json.load(open(index_file))
        adapters = set()
        for task, datasets in adapter_index.items():
            for dataset in datasets.keys():
                for key in datasets[dataset].keys():
                    if key != "default":
                        for org in datasets[dataset][key]["versions"].keys():
                            adapters.add(f"{task}/{dataset}@{org}")
        for adapter in adapters:
            logger.debug(f"Loading adapter {adapter}")
            self.model.load_adapter(adapter, load_as=adapter, with_head=True, cache_dir=transformers_cache)

    # def _load_single_adapter(self, adapter_name: str):
    #     if adapter_name not in self.model.config.adapters.adapters:
    #         logger.info(f"Loading new adapter {adapter_name}")
    #         self.model.load_adapter(adapter_name, with_head=True, load_as=adapter_name)
    #     else:
    #         logger.debug(f"Adapter {adapter_name} is already loaded. Not loading again")

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._token_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v:k for k,v in label2id.items()}
        prediction.task_outputs["id2label"] = id2label

        return prediction

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._sequence_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v:k for k,v in label2id.items()}
        prediction.task_outputs["id2label"] = id2label

        return prediction

    async def predict(self, request: PredictionRequest) -> PredictionOutput:
        if request.is_preprocessed:
            ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")

        if not request.adapter_name or request.adapter_name not in self.model.config.adapters.adapters:
            ValueError(f"Unknown or missing adapter {request.adapter_name}. "
                       f"Please provider a fully specified adapter name from adapterhub.ml")
        self.model.set_active_adapters(request.adapter_name)

        if request.task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif request.task == Task.token_classification:
            return self._token_classification(request)
        elif request.task == Task.question_answering:
            return self._question_answering(request)
        elif request.task == Task.embedding:
            return self._embedding(request)
        elif request.task == Task.generation:
            return self._generation(request)

