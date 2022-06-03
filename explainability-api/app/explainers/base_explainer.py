import numpy as np
from abc import ABC
from typing import List, Tuple, Dict

import torch
from torch import backends
from torch.nn import Module, ModuleList
from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer
)


class BaseExplainer(ABC):
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
    ):
        self.model = model
        self.tokenizer = tokenizer

        if self.model.config.model_type == "gpt2":
            self.ref_token_id = self.tokenizer.eos_token_id
        else:
            self.ref_token_id = self.tokenizer.pad_token_id

        self.sep_token_id = (
            self.tokenizer.sep_token_id if self.tokenizer.sep_token_id is not None else self.tokenizer.eos_token_id
        )
        self.cls_token_id = (
            self.tokenizer.cls_token_id if self.tokenizer.cls_token_id is not None else self.tokenizer.bos_token_id
        )

        self.model_prefix = model.base_model_prefix

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.word_embeddings = self.model.get_input_embeddings()
        self.position_embeddings = None
        self.token_type_embeddings = None

    def _ensure_tensor_on_device(self, **inputs):
        """
        Ensure PyTorch tensors are on the specified device.

        Args:
            inputs (keyword arguments that should be :obj:`torch.Tensor`): The tensors to place on :obj:`self.device`.

        Return:
            :obj:`Dict[str, torch.Tensor]`: The same as :obj:`inputs` but on the proper device.
        """
        return {name: tensor.to(self.model.device) for name, tensor in inputs.items()}

    def get_model_embeddings(self,
                             embedding_type: str = "word_embeddings"
                             ) -> Module or ModuleList:
        """
        Get the model embedding layer
        :param embedding_type: can be one of word_embeddings, token_type_embeddings or position_embeddings
        :return:
        """
        embeddings = Module or ModuleList
        model_prefix = self.model.base_model_prefix
        model_base = getattr(self.model, model_prefix)
        model_embeddings = getattr(model_base, "embeddings")
        if embedding_type == "word_embeddings":
            embeddings = model_embeddings.word_embeddings
        elif embedding_type == "token_type_embeddings":
            embeddings = model_embeddings.token_type_embeddings
        elif embedding_type == "position_embeddings":
            embeddings = model_embeddings.position_embeddings
        # print(embeddings)
        return embeddings

    def _register_hooks(self, embeddings_list: List):
        """
        Register the model embeddings during the forward pass
        :param embeddings_list:
        :return:
        """

        def forward_hook(module, inputs, output):
            embeddings_list.append(output.squeeze(0).clone().detach())

        handles = []
        embedding_layer = self.get_model_embeddings()
        handles.append(embedding_layer.register_forward_hook(forward_hook))
        return handles

    def _register_embedding_gradient_hooks(self, embedding_grads: List):
        """
        Register the model gradients during the backward pass
        :param embedding_grads:
        :return:
        """
        def hook_layers(module, grad_in, grad_out):
            grads = grad_out[0]
            embedding_grads.append(grads)

        hooks = []
        embedding_layer = self.get_model_embeddings()
        hooks.append(embedding_layer.register_backward_hook(hook_layers))
        return hooks

    def get_gradients(self, inputs, answer_start, answer_end):
        """
        Compute model gradients
        :param inputs: list of question and context
        :param answer_start: answer span start
        :param answer_end: answer span end
        :return: dict of model gradients
        """
        embedding_gradients: List[torch.Tensor] = []
        # print(answer_start, answer_end)

        original_param_name_to_requires_grad_dict = {}
        for param_name, param in self.model.named_parameters():
            original_param_name_to_requires_grad_dict[param_name] = param.requires_grad
            param.requires_grad = True

        hooks: List = self._register_embedding_gradient_hooks(embedding_gradients)
        with backends.cudnn.flags(enabled=False):
            encoded_inputs = self.encode(inputs, return_tensors="pt")
            encoded_inputs.to(self.device)
            outputs = self.model(
                **encoded_inputs,
                start_positions=answer_start.to(self.device),
                end_positions=answer_end.to(self.device)
            )
            loss = outputs.loss

            # Zero gradients.
            # NOTE: this is actually more efficient than calling `self._model.zero_grad()`
            # because it avoids a read op when the gradients are first updated below.
            for p in self.model.parameters():
                p.grad = None
            loss.backward()

        for hook in hooks:
            hook.remove()

        grad_dict = dict()
        for idx, grad in enumerate(embedding_gradients):
            key = "grad_input_" + str(idx + 1)
            grad_dict[key] = grad.detach().cpu().numpy()

        # restore the original requires_grad values of the parameters
        for param_name, param in self.model.named_parameters():
            param.requires_grad = original_param_name_to_requires_grad_dict[param_name]
        # print(grad_dict)
        return grad_dict

    def encode(self, inputs: list = None, add_special_tokens: bool = True, return_tensors=None):
        """
        Encode inputs using the model tokenizer
        :param inputs: question, context pair as a list
        :param add_special_tokens: where to add CLS, SEP tokens
        :param return_tensors: whether to return tensors
        :return: tokenized inputs
        """
        return self.tokenizer(inputs, add_special_tokens=add_special_tokens, return_tensors=return_tensors,
                              padding=True, truncation=True, max_length=512)

    def decode(self, input_ids: torch.Tensor, skip_special_tokens: bool) -> List[str]:
        """
        Decode received input_ids into a list of word tokens.
        Args:
            input_ids (torch.Tensor): Input ids representing
            word tokens for a sentence/document.
        """
        return self.tokenizer.convert_ids_to_tokens(input_ids[0], skip_special_tokens=skip_special_tokens)

    def _predict(
            self,
            inputs,
            ) -> tuple:
        """
        Inference on the input.
        Returns:
             The model outputs and optionally the input features
        """
        encoded_inputs = self.encode(inputs, add_special_tokens=True, return_tensors="pt")
        encoded_inputs.to(self.device)
        if self.model.config.model_type == "roberta":
            self.decoded_text = [token.replace("Ġ", "") for token in self.decode(encoded_inputs["input_ids"],
                                                                                 skip_special_tokens=False)]
        else:
            self.decoded_text = self.decode(encoded_inputs["input_ids"], skip_special_tokens=False)
        self.words_mapping = encoded_inputs.words()

        all_predictions = list()
        self.model.to(self.device)
        predictions = self.model(
            **encoded_inputs
        )
        # print(predictions)
        all_predictions.append(predictions)
        keys = all_predictions[0].keys()
        final_prediction = {}
        for key in keys:
            if isinstance(all_predictions[0][key], tuple):
                tuple_of_lists = list(
                    zip(*[[torch.stack(p).cpu() if isinstance(p, tuple) else p.cpu() for p in tpl[key]] for tpl in
                          all_predictions]))
                final_prediction[key] = tuple(torch.cat(l) for l in tuple_of_lists)
            else:
                final_prediction[key] = torch.cat([p[key].to(self.device) for p in all_predictions])
        # print("predictions: ", final_prediction)
        return final_prediction["start_logits"], final_prediction["end_logits"], encoded_inputs

    def question_answering(self, request):
        """
        Span-based question answering for a given question and context.
        We expect the input to use the (question, context) format for the text pairs.

        Args:
          request: the prediction request

        """

        def decode(start_: np.ndarray,
                   end_: np.ndarray,
                   topk: int,
                   max_answer_len: int,
                   undesired_tokens_: np.ndarray) -> Tuple:
            """
            Take the output of any :obj:`ModelForQuestionAnswering` and will generate probabilities
            for each span to be the actual answer.

            In addition, it filters out some unwanted/impossible cases like answer len being greater
            than max_answer_len or answer end position being before the starting position. The method
            supports output the k-best answer through the topk argument.

            Args:
                start_ (:obj:`np.ndarray`): Individual start probabilities for each token.
                end (:obj:`np.ndarray`): Individual end_ probabilities for each token.
                topk (:obj:`int`): Indicates how many possible answer span(s) to extract from the model output.
                max_answer_len (:obj:`int`): Maximum size of the answer to extract from the model's output.
                undesired_tokens_ (:obj:`np.ndarray`): Mask determining tokens that can be part of the answer
            """
            # Ensure we have batch axis
            if start_.ndim == 1:
                start_ = start_[None]

            if end_.ndim == 1:
                end_ = end_[None]

            # Compute the score of each tuple(start_, end_) to be the real answer
            outer = np.matmul(np.expand_dims(start_, -1), np.expand_dims(end_, 1))

            # Remove candidate with end_ < start_ and end_ - start_ > max_answer_len
            candidates = np.tril(np.triu(outer), max_answer_len - 1)

            #  Inspired by Chen & al. (https://github.com/facebookresearch/DrQA)
            scores_flat = candidates.flatten()
            if topk == 1:
                idx_sort = [np.argmax(scores_flat)]
            elif len(scores_flat) < topk:
                idx_sort = np.argsort(-scores_flat)
            else:
                idx = np.argpartition(-scores_flat, topk)[0:topk]
                idx_sort = idx[np.argsort(-scores_flat[idx])]

            starts_, ends_ = np.unravel_index(idx_sort, candidates.shape)[1:]
            desired_spans = np.isin(starts_, undesired_tokens_.nonzero()) & np.isin(ends_, undesired_tokens_.nonzero())
            starts_ = starts_[desired_spans]
            ends_ = ends_[desired_spans]
            scores_ = candidates[0, starts_, ends_]

            return starts_, ends_, scores_

        start_logits, end_logits, features = self._predict(request)
        # print(features)
        task_outputs = {"answers": []}
        for idx, (start, end, (_, context)) in enumerate(zip(start_logits, end_logits, request)):
            start = start.cpu().detach().numpy()
            end = end.cpu().detach().numpy()
            # Ensure padded tokens & question tokens cannot belong to the set of candidate answers.
            question_tokens = np.abs(np.array([s != 1 for s in features.sequence_ids(idx)]) - 1)
            # Unmask CLS token for 'no answer'
            question_tokens[0] = 1
            undesired_tokens = question_tokens & features["attention_mask"][idx].numpy()

            # Generate mask
            undesired_tokens_mask = undesired_tokens == 0.0

            # Make sure non-context indexes in the tensor cannot contribute to the softmax
            start = np.where(undesired_tokens_mask, -10000.0, start)
            end = np.where(undesired_tokens_mask, -10000.0, end)

            start = np.exp(start - np.log(np.sum(np.exp(start), axis=-1, keepdims=True)))
            end = np.exp(end - np.log(np.sum(np.exp(end), axis=-1, keepdims=True)))

            # print(start, end)

            # Get score for 'no answer' then mask for decoding step (CLS token
            no_answer_score = (start[0] * end[0]).item()
            start[0] = end[0] = 0.0

            starts, ends, scores = decode(
                start, end, 1, 128, undesired_tokens
            )
            enc = features[idx]
            answers = [
                {
                    "score": score.item(),
                    "start": enc.word_to_chars(
                        enc.token_to_word(s), sequence_index=1)[0],
                    "end": enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1],
                    "answer": context[
                              enc.word_to_chars(enc.token_to_word(s), sequence_index=1)[0]:
                              enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1]],
                }
                for s, e, score in zip(starts, ends, scores)]
            answers.append({"score": no_answer_score, "start": 0, "end": 0, "answer": ""})
            answers = sorted(answers, key=lambda x: x["score"], reverse=True)[:1]
            task_outputs["answers"].append(answers)
        return task_outputs

    def process_outputs(self, attributions: Dict, top_k: int, mode: str) -> Dict:
        """
        post-process the word attributions to merge the sub-words tokens
        to words
        """

        dec_text = self.decoded_text
        word_map = self.words_mapping

        words = [dec_text[0]]
        for idx, (word_idx, word) in enumerate(zip(word_map, dec_text[1:])):
            if word_idx == word_map[idx + 1] and not word == self.tokenizer.sep_token:
                words[-1] = f'{words[-1]}{word.replace("##", "")}'
            else:
                words.append(word)

        c_list = [1]
        attr = [attributions[0]]
        for idx, (word_idx, score) in enumerate(zip(word_map, attributions[1:])):
            if word_idx == word_map[idx + 1] and word_idx is not None:
                attr[-1] = attr[-1] + score
                c_list[-1] = c_list[-1] + 1
            else:
                attr.append(score)
                c_list.append(1)

        assert len(words) == len(attr)
        imp = [sum_imp / length for length, sum_imp in zip(c_list, attr)]
        normed_imp = [np.round(float(i) / sum(imp), 3) for i in imp]
        result = {w: a for w, a in zip(words, normed_imp)}

        filter_idx = list(result.keys()).index(self.tokenizer.sep_token)
        question = {v[0]: v[1] for idx, v in enumerate(result.items()) if idx < filter_idx}
        context = {v[0]: v[1] for idx, v in enumerate(result.items()) if idx > filter_idx}
        question.pop(self.tokenizer.cls_token)

        if mode == "question":
            outputs = {k: v for k, v in sorted(question.items(),
                                               key=lambda item: item[1],
                                               reverse=True)[:top_k]}
        elif mode == "context":
            outputs = {k: v for k, v in sorted(context.items(),
                                               key=lambda item: item[1],
                                               reverse=True)[:top_k]}
        elif mode == "all":
            outputs_question = {k: v for k, v in sorted(question.items(),
                                                        key=lambda item: item[1],
                                                        reverse=True)[:top_k]}
            outputs_context = {k: v for k, v in sorted(context.items(),
                                                       key=lambda item: item[1],
                                                       reverse=True)[:top_k]}
            outputs = {"question": outputs_question, "context": outputs_context}
        else:
            raise ValueError("Method not allowed")
        return outputs
