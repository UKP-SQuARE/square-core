from abc import ABC
from collections import defaultdict

from transformers import AutoTokenizer

from .transformer import Transformer
import torch
import onnxruntime
import numpy as np
from typing import Union, Tuple
from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.models.prediction import PredictionOutput, PredictionOutputForEmbedding, \
    PredictionOutputForSequenceClassification, PredictionOutputForGeneration, PredictionOutputForTokenClassification


def to_numpy(x):
    if type(x) is not np.ndarray:
        x = x.detach().cpu().numpy() if x.requires_grad else x.cpu().numpy()
    return x


class Onnx(Transformer):
    def __init__(self, model_path: str, model_name: str, batch_size: int, disable_gpu: bool,
                 max_input_size: int, **kwargs) -> None:
        # This assumes that a corresponding onnx file exists
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.session = onnxruntime.InferenceSession(model_path)
        self.batch_size = batch_size
        self.diable_gpu = disable_gpu
        self.max_input_size = max_input_size

    def _predict(self, request: PredictionRequest, output_features=False, features=None) \
            -> Union[dict, Tuple[dict, dict]]:
        """
        Inference on the input.
        :param request: the request with the input and optional kwargs
        :param output_features: return the features of the input.
        Necessary if, e.g., attention mask is needed for post-processing.
        :return: The model outputs and optionally the input features
        """
        all_predictions = []
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get("padding", True)
        request.preprocessing_kwargs["truncation"] = request.preprocessing_kwargs.get("truncation", True)
        if features is None:
            features = self.tokenizer(request.input,
                                      return_tensors="pt",
                                      **request.preprocessing_kwargs)
        # feature_ids = torch.tensor(features["input_ids"])
        for start_idx in range(0, features["input_ids"].shape[0], self.batch_size):
            input_names = [self.session.get_inputs()[i].name for i in range(len(self.session.get_inputs()))]
            ort_inputs = dict(
                (k, to_numpy(input_data[start_idx:start_idx + self.batch_size])) for k, input_data in features.items()
                if k in input_names)
            res = self.session.run([], ort_inputs)
            all_predictions.append(res)
        final_prediction = {}
        output_names = [self.session.get_outputs()[i].name for i in range(len(self.session.get_outputs()))]
        for idx, key in enumerate(output_names):
            # HuggingFace outputs for 'attentions' and more is returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values' which is only relevant for generation.
            # Generation should NOT use this function
            final_prediction[key] = torch.cat([torch.tensor(p[idx]) for p in all_predictions])
        if output_features:
            return final_prediction, features
        return final_prediction

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        """
        Embeds the input from the request
        :param request: The request containing input and optionally task kwargs like embedding method
        :return: The embedding output
        """
        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(
                f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}")

        task_outputs = {
            "embedding_mode": embedding_mode
        }
        predictions, features = self._predict(request, output_features=True)

        if embedding_mode == "pooler":
            if "pooler_output" not in predictions:
                raise ValueError("No pooler output available. Use a different model or an other embedding method")
            emb = predictions["pooler_output"]
        else:
            if "last_hidden_state" not in predictions:
                raise ValueError("No last hidden state available. Use a different model or the pooler embedding method")
            hidden_state = predictions["last_hidden_state"]
            attention_mask = features["attention_mask"]
            if embedding_mode == "cls":
                emb = hidden_state[:, 0, :]
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
                task_outputs["word_ids"] = [features.word_ids(i) for i in range(len(request.input))]
        predictions["embeddings"] = emb

        return PredictionOutputForEmbedding(model_outputs=predictions, **task_outputs)

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies the given input
        :param request: The request containing e.g. the input text
        :return: The prediction output contaiing the predicted labels
        """
        predictions = self._predict(request)
        task_outputs = {}
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("is_regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()

        return PredictionOutputForSequenceClassification(model_outputs=predictions, **task_outputs)

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies each token of the input text
        :param request: The request containing e.g. the input text
        :return: the classification output containing the labels
        """
        predictions, features = self._predict(request, output_features=True)
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        task_outputs = {
            "word_ids": [features.word_ids(i) for i in range(len(request.input))]
        }
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("is_regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()

        return PredictionOutputForTokenClassification(model_outputs=predictions, **task_outputs)

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        """
        Generates a continuation for the given input sequence
        :param request: The request with e.g. the input sequence
        :return: The output containing the generated text
        """
        max_length = request.task_kwargs.get("max_length", 20)
        eos_token_id = self.tokenizer.eos_token_id if self.tokenizer.eos_token_id is not None else self.tokenizer.pad_token_id
        task_outputs = {"generated_texts": []}
        model_outputs = defaultdict(list)
        for prompt in request.input:
            cur_len = 0
            request.preprocessing_kwargs["padding"] = False
            features = self.tokenizer(prompt,
                                      return_tensors="pt",
                                      **request.preprocessing_kwargs)
            input_ids = features["input_ids"]
            attention_mask = features["attention_mask"]
            unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
            scores = ()

            # greedy generation (adapted from transformers/generation_utils.py)
            while cur_len < max_length:
                features = {"input_ids": input_ids, "attention_mask": attention_mask}

                predictions = self._predict(request, features=features)

                next_token_logits = predictions["logits"][:, -1, :]
                scores += (next_token_logits,)

                # argmax
                next_tokens = torch.argmax(next_token_logits, dim=-1)

                # update generated ids, model inputs, and length for next step
                input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
                attention_mask = torch.cat(
                    [attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1
                )
                cur_len = cur_len + 1

                if eos_token_id is not None:
                    unfinished_sequences = unfinished_sequences.mul((next_tokens != eos_token_id).long())

                    # stop when each sentence is finished, or if we exceed the maximum length
                if unfinished_sequences.max() == 0:
                    break

            generated_texts = [self.tokenizer.decode(seq, skip_special_tokens=True,
                                                     clean_up_tokenization_spaces=request.task_kwargs.get(
                                                         "clean_up_tokenization_spaces", False))
                               for seq in input_ids]
            task_outputs["generated_texts"].append(generated_texts)

            res = {
                "sequence": input_ids,
                "scores": scores,
            }
            for key in res.keys():
                model_outputs[key].append(res[key])

        return PredictionOutputForGeneration(model_outputs=model_outputs, **task_outputs)
