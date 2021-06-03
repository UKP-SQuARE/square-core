import json
from typing import Union, Tuple

import torch
from loguru import logger

from transformers import AutoTokenizer, AutoModel

from square_model_inference.inference.model import Model
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput
from square_model_inference.core.config import MODEL_NAME, DISABLE_GPU, MAX_BATCH_SIZE


class Transformer(Model):
    SUPPORTED_EMBEDDING_MODES = ["mean", "max", "cls", "token"]

    def __init__(self):
        self._load_model(AutoModel)

    def _load_model(self, model_cls):
        """
        Load the base model MODEL_NAME and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or environment variable DISABLE_GPU is true.
        """
        logger.debug(f"Loading model {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # Check if GPU is available
        device = "cuda" if torch.cuda.is_available() and not DISABLE_GPU else "cpu"
        model = model_cls.from_pretrained(MODEL_NAME).to(device)
        logger.info(f"Model {MODEL_NAME} loaded on {device}")

        self.model = model
        self.tokenizer = tokenizer

    def _ensure_tensor_on_device(self, **inputs):
        """
        Ensure PyTorch tensors are on the specified device.

        Args:
            inputs (keyword arguments that should be :obj:`torch.Tensor`): The tensors to place on :obj:`self.device`.

        Return:
            :obj:`Dict[str, torch.Tensor]`: The same as :obj:`inputs` but on the proper device.
        """
        return {name: tensor.to(self.model.device) for name, tensor in inputs.items()}

    def _predict(self, request: PredictionRequest, output_word_ids=False, output_attention_mask=False) \
            -> Union[dict, Tuple[dict, dict]]:
        all_predictions = []
        features = self.tokenizer(request.input,
                                  return_tensors="pt",
                                  padding=True,
                                  truncation=True,
                                  **request.preprocessing_kwargs)
        for start_idx in range(0, len(request.input), MAX_BATCH_SIZE):
            with torch.no_grad():
                input_features = {k: features[k][start_idx:start_idx+MAX_BATCH_SIZE] for k in features.keys()}
                input_features = self._ensure_tensor_on_device(**input_features)
                predictions = self.model(**input_features, **request.model_kwargs)
                all_predictions.append(predictions)
        keys = all_predictions[0].keys()
        final_prediction = {}
        for key in keys:
            # HuggingFace outputs for 'attentions' and more is returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values' which is only relevant for generation.
            # Generation should NOT use this function
            if isinstance(all_predictions[0][key], tuple):
                tuple_of_lists = list(zip(*[[p.cpu() for p in tpl[key]] for tpl in all_predictions]))
                final_prediction[key] = tuple(torch.cat(l) for l in tuple_of_lists)
            else:
                final_prediction[key] = torch.cat([p[key].cpu() for p in all_predictions])
        if any((output_word_ids, output_attention_mask)):
            word_ids = [features.word_ids(i) for i in range(len(request.input))]
            attention_mask = features["attention_mask"]
            return final_prediction, {"word_ids": word_ids, "attention_mask": attention_mask}
        return final_prediction

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        request.model_kwargs["output_hidden_states"] = True
        predictions, other = self._predict(request, output_word_ids=True, output_attention_mask=True)
        hidden_state = predictions.pop("hidden_states")[-1]
        attention_mask = other["attention_mask"]

        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            ValueError(f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}")

        if embedding_mode == "cls":
            emb = hidden_state[:, 0, :]
        # copied from sentence-transformers pooling
        elif embedding_mode == "max":
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            hidden_state[input_mask_expanded == 0] = -1e9  # Set padding tokens to large negative value
            emb = torch.max(hidden_state, 1)[0]
        # copied from sentence-transformers pooling
        elif embedding_mode == "mean":
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            sum_embeddings = torch.sum(hidden_state * input_mask_expanded, 1)
            sum_mask = input_mask_expanded.sum(1)
            emb = sum_embeddings / sum_mask
        elif embedding_mode == "token":
            emb = hidden_state
        predictions["embedding"] = emb
        task_outputs = {
            "embedding_mode": embedding_mode,
            "word_ids": other["word_ids"]
        }
        return PredictionOutput(model_outputs=predictions, task_outputs=task_outputs)

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        predictions, other = self._predict(request, output_word_ids=True)
        # If logits dim > 1 or if the 'regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            predictions["labels"] = torch.argmax(predictions["logits"], dim=-1)
        label2id = self.model.config.label2id
        id2label = {v:k for k,v in label2id.items()}
        task_outputs = {
            "id2label": id2label,
            "word_ids": other["word_ids"]
        }
        return PredictionOutput(model_outputs=predictions, task_outputs=task_outputs)

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        predictions = self._predict(request)
        # If logits dim > 1 or if the 'regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            predictions["labels"] = torch.argmax(predictions["logits"], dim=-1)
        label2id = self.model.config.label2id
        id2label = {v:k for k,v in label2id.items()}
        task_outputs = {
            "id2label": id2label
        }
        return PredictionOutput(model_outputs=predictions, task_outputs=task_outputs)

    async def predict(self, request: PredictionRequest) -> PredictionOutput:
        if request.is_preprocessed:
            ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")

        if request.task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif request.task == Task.token_classification:
            return self._token_classification(request)
        elif request.task == Task.embedding:
            return self._embedding(request)
        elif request.task == Task.generation:
            return self._generation(request)

