import logging
from copy import deepcopy
from typing import Dict, List, Tuple

import numpy as np
from tasks.attacks.attack import Attacker

logger = logging.getLogger(__name__)


class TopkTokens(Attacker):
    def __init__(self, task, request, model_outputs):
        """
        Initialize the input reduction attack

        Args:
            request (dict): the request to the model
            task (Task): the task to attack
            model_outputs (dict): the model outputs
        """
        super().__init__(request, task, model_outputs)
        self.top_k = self.request.attack_kwargs.get("max_tokens", 10)

    def attack_instance(self) -> Tuple[List[List], List]:
        """
        selects topk tokens from the context

        Returns:
            Tuple of reduced inputs and the largest indices
        """

        (
            question_attributions,
            context_attributions,
            question_text,
            context_text,
            _,
            _,
            context_tokens,
            context_scores,
        ) = self._get_tokens_and_attributions()
        topk_indices = np.argsort(context_scores)[::-1][: self.top_k].tolist()

        reduced_instances_and_smallest: List = []
        while len(context_tokens) != 1:
            instance = deepcopy(context_tokens)

            # remove smallest
            smallest = np.argmin(context_scores)
            context_scores = np.delete(context_scores, smallest)
            context_tokens = np.delete(context_tokens, smallest)

            # remove smallest
            inputs_before_smallest = instance[0:smallest]
            inputs_after_smallest = instance[smallest + 1 :]
            reduced_instance = np.append(inputs_before_smallest, inputs_after_smallest)

            reduced_instances_and_smallest.append(" ".join(list(reduced_instance)))

        reduced_contexts = list(reversed(reduced_instances_and_smallest))[: self.top_k]
        prepared_inputs = [
            [q, c]
            for q, c in zip(
                [question_text] * (len(reduced_contexts) + 1),
                [context_text] + reduced_contexts,
            )
        ]

        batch_request = self.base_prediction_request
        batch_request["input"] = prepared_inputs
        saliency_method = self.request.attack_kwargs.get("saliency_method", "attention")
        if saliency_method in ["attention", "scaled_attention"]:
            batch_request["model_kwargs"] = {"output_attentions": True}
        batch_request["contexts"] = [context_text] + reduced_contexts
        return batch_request, topk_indices
