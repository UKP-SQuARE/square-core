import logging
from copy import deepcopy
from typing import Dict, List, Tuple

import numpy as np
from tasks.attacks.attack import Attacker

logger = logging.getLogger(__name__)


class InputReduction(Attacker):
    """
    Reduce the input to the top k words with the highest importance
    """

    def __init__(self, request, task, model_outputs):
        """
        Initialize the input reduction attack

        Args:
            request (dict): the request to the model
            task (Task): the task to attack
            model_outputs (dict): the model outputs

        """
        super().__init__(request, task, model_outputs)
        self.top_k = self.request.attack_kwargs.get("max_reductions", 10)

    def attack_instance(self) -> Tuple[List[List], List]:
        """
        post-process the word attributions to merge the sub-words tokens
        to words

        Returns:
            Tuple of reduced inputs and the smallest indices
        """

        (
            question_attributions,
            context_attributions,
            question_text,
            context_text,
            question_tokens,
            question_scores,
            _,
            _,
        ) = self._get_tokens_and_attributions()

        smallest_indices = np.argsort(question_scores)[: self.top_k].tolist()

        beam = self.top_k
        reduced_instances_and_smallest: List[Tuple] = []
        while len(question_tokens) != 1:
            instance = deepcopy(question_tokens)

            # find smallest
            smallest = np.argmin(question_scores)
            question_scores = np.delete(question_scores, smallest)
            question_tokens = np.delete(question_tokens, smallest)

            # remove smallest
            inputs_before_smallest = instance[0:smallest]
            inputs_after_smallest = instance[smallest + 1 :]
            reduced_instance = np.append(inputs_before_smallest, inputs_after_smallest)

            reduced_instances_and_smallest.append(
                (" ".join(list(reduced_instance)), smallest)
            )
            # decrement top k counter
            beam -= 1
            if beam == 0:
                break

        reduced_questions = [entry[0] for entry in reduced_instances_and_smallest]

        prepared_inputs = self.prepare_data(
            question_text=[question_text] + reduced_questions,
            context_text=[context_text] * (len(reduced_questions) + 1),
        )

        batch_request = self.base_prediction_request
        batch_request["input"] = prepared_inputs
        # method defaults to attention in input reduction
        saliency_method = self.request.attack_kwargs.get("saliency_method", "attention")
        if saliency_method in ["attention", "scaled_attention"]:
            batch_request["model_kwargs"] = {"output_attentions": True}
        batch_request["explain_kwargs"] = {
            "method": saliency_method,
            "top_k": len(question_text),  # set to a max value to get all words
            "mode": "all",
        }
        batch_request["questions"] = [question_text] + reduced_questions

        return batch_request, smallest_indices
