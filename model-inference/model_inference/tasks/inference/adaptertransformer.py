import logging
import os
import torch
import collections

from model_inference.tasks.config.model_config import model_config
from model_inference.tasks.models.prediction import PredictionOutput
from model_inference.tasks.models.request import PredictionRequest, Task
from transformers.adapters import AutoAdapterModel, list_adapters
from transformers.adapters.heads import CausalLMHead

from .transformer import Transformer


logger = logging.getLogger(__name__)


class AdapterTransformer(Transformer):
    """
    The class for all adapter-based models using the adapter-transformers package
    """

    def __init__(self, **kwargs):
        """
        Initialize the Adapter with its underlying Transformer
        and pre-load all available adapters from adapterhub.ml

        Args:
             model_name: the Huggingface model name
             disable_gpu: do not move model to GPU even if CUDA is available
             transformers_cache: Should be same as TRANSFORMERS_CACHE
                env variable. This folder will be used to store the adapters
             kwargs: Not used
        """
        self.task = None
        self.gradients = None
        self._load_model(
            AutoAdapterModel, model_config.model_name, model_config.disable_gpu
        )
        if model_config.preloaded_adapters:
            self._load_adapter(model_config.model_name, model_config.transformers_cache)
        self.model_name = model_config.model_name

    def _load_adapter(self, model_name, transformers_cache):
        """
        Pre-load all available adapters for MODEL_NAME from adapterhub.ml.
        We parse the hub index to extract all names and then load each model.

        Args:
             model_name: the Huggingface model name
             transformers_cache: Should be same as TRANSFORMERS_CACHE env variable.
                This folder will be used to store the adapters

        """

        logger.info("Loading all available adapters")
        adapter_infos = []
        for source in ["ah", "hf"]:
            adapter_infos = [
                info
                for info in list_adapters(source=source)
                if info.model_name == model_name
            ]
            if source == "ah":
                adapters = set(
                    f"{adapter_info.task}/{adapter_info.subtask}@{adapter_info.username}"
                    for adapter_info in adapter_infos
                )
            elif source == "hf":
                adapters = set(
                    f"{adapter_info.adapter_id}"
                    for adapter_info in adapter_infos
                    if adapter_info.adapter_id.startswith("AdapterHub")
                    or adapter_info.adapter_id.startswith("UKP-SQuARE")
                )
            for adapter in adapters:
                logger.debug(f"Loading adapter {adapter}")
                try:
                    self.model.load_adapter(
                        adapter,
                        load_as=adapter,
                        with_head=True,
                        cache_dir=transformers_cache,
                        source=source,
                    )
                except RuntimeError as e:
                    if "Error(s) in loading state_dict" in e.args[0]:
                        logger.debug(
                            f"Could not load {adapter} due to missing label_ids in "
                            f"config resulting in exception:\n{e.args[0]}"
                        )
                    else:
                        raise e
                except AttributeError as e:
                    if "Given head type " in e.args[0]:
                        logger.debug(
                            f"Could not load {adapter} due to unknown head type:\n{e.args[0]}"
                        )
                    else:
                        raise e
        # Move all freshly loaded adapter weights to the same device as the model
        self.model.to(self.model.device)

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id
        # (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._token_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v: k for k, v in label2id.items()}
        prediction.id2label = id2label

        return prediction

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from
        # config.label2id (what super() uses) to the mapping
        # of the chosen head
        logger.info(f"sequence classification request:\n{request.json()}")
        self.model.config.prediction_heads[request.adapter_name]["num_choices"] = len(
            request.input
        )
        logger.info(
            f"num_choices: {self.model.config.prediction_heads[request.adapter_name]['num_choices']}"
        )
        prediction = super()._sequence_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v: k for k, v in label2id.items()}
        prediction.id2label = id2label

        logger.info(f"sequence classification prediction:\n{prediction.labels}")
        return prediction

    def _prepare_adapter(self, adapter_name, model_kwargs):
        """
        Prepare the adapter for inference by setting it as the active adapter
        """
        # check if adapter name is a list of string or sting of adapters and is not empty
        if adapter_name and isinstance(adapter_name, str):
            adapter_name = [adapter_name]

        # check if test stage is set to true
        if os.environ.get("TEST", 0) == 0:
            # average adapters
            if len(adapter_name) > 1 and model_kwargs["average_adapters"]:
                logger.info(f"averaging adapters")
                state_dict = {}
                for name in adapter_name:
                    self.model.load_adapter(name, load_as=name, source=None)
                    p_state_dict = self.model.state_dict()
                    state_dict.update(p_state_dict)
                avg_dict = self._average_adapter_params(adapter_name, state_dict)
                logger.info(f"averaging {len(avg_dict)} parameters")
                state_dict.update(avg_dict)

                missing, unexpected = self.model.load_state_dict(
                    state_dict, strict=False
                )
                logger.info(f"{len(missing)} missing, {len(unexpected)} unexpected")
                logger.info(f"missing: {missing}")
                logger.info(f"unexpected: {unexpected}")
                missing = set(missing)
                missing_new = [
                    k
                    for k, p in self.model.named_parameters()
                    if p.requires_grad and k in missing
                ]
                logger.info(f"missing parameters with requires_grad: {missing_new}")
            else:
                adapter_name = adapter_name[0]
                # try deploying adapter from source hf or ah
                # identify adapter source
                source = "hf" if adapter_name.startswith("UKP-SQuARE") else None
                self.model.load_adapter(
                    adapter_name, load_as=adapter_name, source=source
                )
                # check if the adapter is there in the hub
                if (
                    not adapter_name
                    or adapter_name not in self.model.config.adapters.adapters
                ):
                    raise ValueError(
                        f"Unknown or missing adapter {adapter_name}. "
                        f"Please provider a fully specified adapter name from adapterhub.ml"
                    )
        else:
            model_name = "bert-base-uncased"
            adapter_name = adapter_name[0]
            self.model.load_adapter(
                adapter_name,
                model_name=model_name,
                load_as=adapter_name,
                source=None,
            )
        self.model.set_active_adapters(adapter_name)

    def _average_adapter_params(self, adapter_names, state_dict, proportions=None):
        """
        Average multiple adapter weights and return the averaged state_dict
        """
        if proportions is None:
            proportions = {
                a: torch.tensor(1 / len(adapter_names)) for a in adapter_names
            }
        param_lst = collections.defaultdict(list)
        for k, p in state_dict.items():
            for name in adapter_names:
                if f"adapters.{name}." in k:
                    rk = k.replace(f".{name}.", f".adapter.")
                    param_lst[rk].append(p * proportions[name])
                if f"heads.{name}." in k:
                    rk = k.replace(f"heads.{name}.", "head.")
                    param_lst[rk].append(p * proportions[name])
        avg_dict = {
            k: torch.sum(torch.stack(vs, dim=0), dim=0) for k, vs in param_lst.items()
        }
        return avg_dict

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        # ensure that the loaded had is a lm head
        if self.model.active_head is None or not isinstance(
            self.model.active_head, CausalLMHead
        ):
            # if there is no head or a head that is not a lm head add a lm head
            # depending on the model class different heads might be available
            # e.g. GPT2 -> causal lm head, BART -> seq2seq lm head
            if hasattr(self.model, "add_causal_lm_head"):
                self.model.add_causal_lm_head("lm_head", True)
            elif hasattr(self.model, "add_seq2seq_lm_head"):
                self.model.add_seq2seq_lm_head("lm_head", True)
        return super()._generation(request)

    def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError(
                "is_preprocessed=True is not supported for this model. Please use text as input."
            )
        if len(request.input) > model_config.max_input_size:
            raise ValueError(
                f"Input is too large. Max input size is {model_config.max_input_size}"
            )
        self._prepare_adapter(request.adapter_name, request.model_kwargs)

        self.task = task
        if self.task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif self.task == Task.token_classification:
            return self._token_classification(request)
        elif self.task == Task.question_answering:
            return self._question_answering(request)
        elif self.task == Task.embedding:
            return self._embedding(request)
        elif self.task == Task.generation:
            return self._generation(request)
