from collections import defaultdict
from typing import Tuple, Union

import numpy as np
import onnxruntime
import torch
from tasks.config.model_config import model_config
from tasks.models.prediction import (PredictionOutput,
                                     PredictionOutputForEmbedding,
                                     PredictionOutputForGeneration,
                                     PredictionOutputForSequenceClassification,
                                     PredictionOutputForTokenClassification)
from tasks.models.request import PredictionRequest
from torch import nn
from torch.nn import functional as F
from transformers import AutoTokenizer

from .transformer import Transformer


def to_numpy(x):
    if type(x) is not np.ndarray:
        x = x.detach().cpu().numpy() if x.requires_grad else x.cpu().numpy()
    return x


class Onnx(Transformer):
    def __init__(self, **kwargs) -> None:

        """
         Args:
             model_path: path where the model is stored
             model_name: the ONNX model name
             decoder_path: path to the decoder ONNX model
             kwargs: Not used
        """
        # This assumes that a corresponding onnx file exists
        self.tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.session = onnxruntime.InferenceSession(model_config.model_path)
        # check whether a decoder model is available
        self.is_encoder_decoder = (
            model_config.decoder_path is not None and model_config.decoder_path != ""
        )
        if self.is_encoder_decoder:
            # if available load the decoder model in a onnx session
            self.decoder_session = onnxruntime.InferenceSession(
                model_config.decoder_path
            )

    def _predict(
        self, request: PredictionRequest, output_features=False, features=None
    ) -> Union[dict, Tuple[dict, dict]]:
        """
        Inference on the input.

        Args:

             request: the request with the input and optional kwargs
             output_features: return the features of the input. Necessary if, e.g., attention mask is needed for post-processing.

        Returns:
                The model outputs and optionally the input features
        """
        all_predictions = []
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get(
            "padding", True
        )
        request.preprocessing_kwargs["truncation"] = request.preprocessing_kwargs.get(
            "truncation", True
        )
        if features is None:
            features = self.tokenizer(
                request.input, return_tensors="pt", **request.preprocessing_kwargs
            )
        for start_idx in range(
            0, features["input_ids"].shape[0], model_config.batch_size
        ):
            input_names = [
                self.session.get_inputs()[i].name
                for i in range(len(self.session.get_inputs()))
            ]
            ort_inputs = dict(
                (
                    k,
                    to_numpy(
                        input_data[start_idx : start_idx + model_config.batch_size]
                    ),
                )
                for k, input_data in features.items()
                if k in input_names
            )

            res = self.session.run([], ort_inputs)
            if self.is_encoder_decoder:
                if self.decoder_session:
                    # Prepare decoder input
                    # This works with encoder decoder models exported similarirly to the FastT5 onnx model
                    ort_inputs = {
                        "input_ids": features["decoder_input_ids"]
                        if "decoder_input_ids" in features
                        else np.array(
                            [
                                [self.get_bos_token()]
                                for _ in range(features["input_ids"].shape[0])
                            ],
                            dtype=np.int64,
                        ),
                        "encoder_hidden_states": res[0],
                        "encoder_attention_mask": to_numpy(features["attention_mask"]),
                    }
                    res += self.decoder_session.run([], ort_inputs)
            all_predictions.append(res)
        final_prediction = {}
        output_names = [
            self.session.get_outputs()[i].name
            for i in range(len(self.session.get_outputs()))
        ]
        if self.is_encoder_decoder:
            output_names += [
                self.decoder_session.get_outputs()[i].name
                for i in range(len(self.decoder_session.get_outputs()))
            ]

        for idx, key in enumerate(output_names):
            # HuggingFace outputs for 'attentions' and more is returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values' which is only relevant for generation.
            # Generation should NOT use this function
            final_prediction[key] = torch.cat(
                [torch.tensor(p[idx]) for p in all_predictions]
            )
        if output_features:
            return final_prediction, features
        return final_prediction

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        """
        Embeds the input from the request

        Args:
             request: The request containing input and optionally task kwargs like embedding method

        Return:
             The embedding output
        """
        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(
                f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}"
            )

        task_outputs = {"embedding_mode": embedding_mode}
        predictions, features = self._predict(request, output_features=True)

        if embedding_mode == "pooler":
            if "pooler_output" not in predictions:
                raise ValueError(
                    "No pooler output available. Use a different model or an other embedding method"
                )
            emb = predictions["pooler_output"]
        else:
            if "last_hidden_state" not in predictions:
                if "hidden_states" in predictions:
                    hidden_state = predictions["hidden_states"]
                else:
                    raise ValueError(
                        "No last hidden state available. Use a different model or the pooler embedding method"
                    )
            else:
                hidden_state = predictions["last_hidden_state"]
            attention_mask = features["attention_mask"]
            if embedding_mode == "cls":
                emb = hidden_state[:, 0, :]
            elif embedding_mode == "max":
                input_mask_expanded = (
                    attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
                )
                hidden_state[
                    input_mask_expanded == 0
                ] = -1e9  # Set padding tokens to large negative value
                emb = torch.max(hidden_state, 1)[0]
                # copied from sentence-transformers pooling
            elif embedding_mode == "mean":
                input_mask_expanded = (
                    attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
                )
                sum_embeddings = torch.sum(hidden_state * input_mask_expanded, 1)
                sum_mask = input_mask_expanded.sum(1)
                emb = sum_embeddings / sum_mask
            elif embedding_mode == "token":
                emb = hidden_state
                task_outputs["word_ids"] = [
                    features.word_ids(i) for i in range(len(request.input))
                ]
        predictions["embeddings"] = emb

        return PredictionOutputForEmbedding(model_outputs=predictions, **task_outputs)

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies the given input

        Args:
             request: The request containing e.g. the input text

        Returns:
                 The prediction output containing the predicted labels
        """
        predictions = self._predict(request)
        task_outputs = {}
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get(
            "is_regression", False
        ):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(
                predictions["logits"], dim=-1
            ).tolist()

        return PredictionOutputForSequenceClassification(
            model_outputs=predictions, **task_outputs
        )

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies each token of the input text

        Args:
            request: The request containing e.g. the input text

        Returns:
                 the classification output containing the labels
        """
        predictions, features = self._predict(request, output_features=True)
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        task_outputs = {
            "word_ids": [features.word_ids(i) for i in range(len(request.input))]
        }
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get(
            "is_regression", False
        ):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(
                predictions["logits"], dim=-1
            ).tolist()

        return PredictionOutputForTokenClassification(
            model_outputs=predictions, **task_outputs
        )

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        """
        Generates a continuation for the given input sequence

        Args:
             request: The request with e.g. the input sequence

        Returns:
             The output containing the generated text
        """
        max_length = request.task_kwargs.get("max_length", 20)
        task_outputs = {"generated_texts": []}
        model_outputs = defaultdict(list)
        for prompt in request.input:
            # if num_beams is specified beam search is executed otherwise greedy search
            if "num_beams" in request.task_kwargs:
                input_ids, scores = self._beam_search(request, prompt, max_length)
            else:
                input_ids, scores = self._greedy_generation(request, prompt, max_length)

            generated_texts = [
                self.tokenizer.decode(
                    seq,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=request.task_kwargs.get(
                        "clean_up_tokenization_spaces", False
                    ),
                )
                for seq in input_ids
            ]
            task_outputs["generated_texts"].append(generated_texts)

            res = {
                "sequence": input_ids,
                "scores": scores,
            }
            for key in res.keys():
                model_outputs[key].append(res[key])

        return PredictionOutputForGeneration(
            model_outputs=model_outputs, **task_outputs
        )

    def _greedy_generation(self, request, prompt, max_length):
        """
        Performs greedy generation for the prompts

        Args:
             request: the inference request
             prompt: the prompt for the generation
             max_length: the maximum length of the generated sequence
        Returns:
             the ids of the generated sequence and the score
        """
        cur_len = 0
        eos_token_id = (
            self.tokenizer.eos_token_id
            if self.tokenizer.eos_token_id is not None
            else self.tokenizer.pad_token_id
        )
        request.preprocessing_kwargs["padding"] = False
        features = self.tokenizer(
            prompt, return_tensors="pt", **request.preprocessing_kwargs
        )
        input_ids = features["input_ids"]
        generated_ids = [self.get_bos_token()] if self.is_encoder_decoder else []
        unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
        scores = ()
        # greedy generation (adapted from transformers/generation_utils.py)
        while cur_len < max_length:
            input_data = self._prepare_input(features, generated_ids)
            predictions = self._predict(request, features=input_data)

            next_token_logits = predictions["logits"][:, -1, :]
            scores += (next_token_logits,)

            # argmax
            next_tokens = torch.argmax(next_token_logits, dim=-1)
            # update generated ids, model inputs, and length for next step
            generated_ids.append(next_tokens[:, None].item())
            cur_len = cur_len + 1

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    (next_tokens != eos_token_id).long()
                )
                # stop when each sentence is finished, or if we exceed the maximum length
            if unfinished_sequences.max() == 0:
                break
        return [generated_ids], scores

    def _prepare_input(self, encoder_features, generated_sequence):
        """
        Prepares the input for the _predict method. If the model is an encoder decoder model the
        generated sequence is the decoder input.

        Args:
             encoder_features: the features of the prompt
             generated_sequence: the generated ids

        Returns:
             the features for the model
        """
        model_input = encoder_features.copy()
        # if it is a encoder decoder model the generated sequence is passed to the decoder
        # otherwise the generated sequence is appended to the input_ids
        if self.is_encoder_decoder:
            model_input["decoder_input_ids"] = np.array(
                [generated_sequence], dtype=np.int64
            )
            model_input["decoder_attention_mask"] = np.array(
                [[1] * len(generated_sequence)], dtype=np.int64
            )

        elif generated_sequence:
            model_input["input_ids"] = torch.cat(
                (
                    encoder_features["input_ids"],
                    torch.tensor(generated_sequence).unsqueeze(dim=0),
                ),
                dim=1,
            )
            model_input["attention_mask"] = torch.ones(
                model_input["input_ids"].shape, dtype=torch.int64
            )

        return model_input

    def _beam_search(self, request, prompt, max_length):
        """
        Performs beam search for the given prompt

        Args:
             request: the inference request
             prompt: the generation prompt
             max_length: the maximum length of the generated sequence

        Returns:
             the generated sequence(s)
        """
        request.preprocessing_kwargs["padding"] = False
        features = self.tokenizer(
            prompt, return_tensors="pt", **request.preprocessing_kwargs
        )
        # get the generation arguments
        num_beams = request.task_kwargs.pop("num_beams")
        no_repeat_ngram_size = request.task_kwargs.pop("no_repeat_ngram_size", 0)
        do_sample = request.task_kwargs.pop("do_sample", False)
        top_p = request.task_kwargs.pop("top_p", None)
        top_k = request.task_kwargs.pop("top_k", None)
        num_return_sequences = request.task_kwargs.pop("num_return_sequences", 1)
        return_sequences = []
        for i in range(num_return_sequences):
            sequences = [
                ([self.get_bos_token()] if self.is_encoder_decoder else [], 0.0)
            ]
            cur_len = 0
            while cur_len < max_length:
                candidates = []
                for seq in sequences:
                    model_input = self._prepare_input(features, seq[0])
                    predictions = self._predict(request, False, model_input)

                    next_token_logits = predictions["logits"][:, -1, :]
                    next_token_scores = F.softmax(next_token_logits, dim=1)
                    if do_sample:
                        next_token_scores = self._preprocess_logits(
                            next_token_scores,
                            top_k=top_k,
                            top_p=top_p,
                            min_tokens_to_keep=2 * num_beams,
                        )

                    if no_repeat_ngram_size > 0:
                        banned_batch_tokens = calc_banned_ngram_tokens(
                            torch.tensor([seq[0]]), 1, no_repeat_ngram_size, cur_len
                        )
                        for i, banned_tokens in enumerate(banned_batch_tokens):
                            next_token_scores[i, banned_tokens] = -float("inf")

                    if do_sample:
                        # draw the next token based on the probabilities
                        probs = nn.functional.softmax(next_token_scores, dim=-1)

                        next_tokens = torch.multinomial(
                            probs, num_samples=2 * num_beams
                        )
                        next_token_prob = torch.gather(
                            next_token_scores, -1, next_tokens
                        )

                        _, _indices = torch.sort(
                            next_token_prob, descending=True, dim=1
                        )
                        next_tokens_idx = torch.gather(next_tokens, -1, _indices)

                    else:
                        # take the most likely tokens as the next tokens
                        next_token_prob, next_tokens_idx = torch.topk(
                            next_token_scores, num_beams, dim=-1
                        )
                    candidates += [
                        (seq[0] + [token_id], seq[1] + np.log(score))
                        for token_id, score in zip(
                            next_tokens_idx.squeeze().tolist(),
                            next_token_prob.squeeze().tolist(),
                        )
                    ]
                # select the candidates with the highest scores as beams for the generation of the next token
                sequences = sorted(candidates, key=lambda x: x[1], reverse=True)[
                    :num_beams
                ]
                cur_len += 1

            return_sequences.append(sequences[0])

        return (
            [torch.tensor(s[0]) for s in return_sequences],
            [s[1] for s in return_sequences],
        )

    def get_bos_token(self):
        """
        Depending on the model the beginning of sentence token id can be different or not provided.

        Returns:
             beginning of sentence token id
        """
        if self.tokenizer.bos_token_id is not None:
            return self.tokenizer.bos_token_id
        # if no bos token is available use the padding token
        else:
            return self.tokenizer.pad_token_id

    def _preprocess_logits(
        self,
        scores,
        top_k=None,
        top_p=None,
        min_tokens_to_keep=1,
        filter_value=-float("Inf"),
    ):
        """
        Sets the scores for all tokens that are not in top_p and top_k to the filter value (default = -inf).
        Adapted from huggingface/transformers/generation_logits_process.py

        Args:
             scores:the initial scores for each token
             top_k: the top_k threshold
             top_p: the top_p threshold
             min_tokens_to_keep: the min_number_of_tokens_to_keep
             filter_value: the value to replace the scores with

        Returns:
             the processed scores
        """
        if top_k is not None and top_k != 0:
            top_k = min(max(top_k, min_tokens_to_keep), scores.size(-1))  # Safety check
            # Remove all tokens with a probability less than the last token of the top-k
            indices_to_remove = scores < torch.topk(scores, top_k)[0][..., -1, None]
            scores = scores.masked_fill(indices_to_remove, filter_value)
        if top_p is not None and top_p < 1.0:
            sorted_logits, sorted_indices = torch.sort(scores, descending=True)
            cumulative_probs = sorted_logits.softmax(dim=-1).cumsum(dim=-1)

            # Remove tokens with cumulative top_p above the threshold (token with 0 are kept)
            sorted_indices_to_remove = cumulative_probs > top_p
            if min_tokens_to_keep > 1:
                # Keep at least min_tokens_to_keep (set to min_tokens_to_keep-1 because we add the first one below)
                sorted_indices_to_remove[..., : min_tokens_to_keep - 1] = 0
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[
                ..., :-1
            ].clone()
            sorted_indices_to_remove[..., 0] = 0

            # scatter sorted tensors to original indexing
            indices_to_remove = sorted_indices_to_remove.scatter(
                1, sorted_indices, sorted_indices_to_remove
            )
            scores = scores.masked_fill(indices_to_remove, filter_value)

        return scores


def calc_banned_ngram_tokens(
    prev_input_ids, num_hypos: int, no_repeat_ngram_size: int, cur_len: int
) -> None:
    """Copied from fairseq for no_repeat_ngram in beam_search"""
    if cur_len + 1 < no_repeat_ngram_size:
        # return no banned tokens if we haven't generated no_repeat_ngram_size tokens yet
        return [[] for _ in range(num_hypos)]
    generated_ngrams = [{} for _ in range(num_hypos)]
    for idx in range(num_hypos):
        gen_tokens = prev_input_ids[idx].tolist()
        generated_ngram = generated_ngrams[idx]
        for ngram in zip(*[gen_tokens[i:] for i in range(no_repeat_ngram_size)]):
            prev_ngram_tuple = tuple(ngram[:-1])
            generated_ngram[prev_ngram_tuple] = generated_ngram.get(
                prev_ngram_tuple, []
            ) + [ngram[-1]]

    def _get_generated_ngrams(hypo_idx):
        # Before decoding the next token, prevent decoding of ngrams that have already appeared
        start_idx = cur_len + 1 - no_repeat_ngram_size
        ngram_idx = tuple(prev_input_ids[hypo_idx, start_idx:cur_len].tolist())
        return generated_ngrams[hypo_idx].get(ngram_idx, [])

    banned_tokens = [_get_generated_ngrams(hypo_idx) for hypo_idx in range(num_hypos)]
    return banned_tokens
