from typing import List, Dict, Tuple
from copy import deepcopy
import numpy as np
import logging


logger = logging.getLogger(__name__)


class InputReduction:
    def __init__(
        self, top_k,
    ):
        self.top_k = top_k

    def reduce_instance(self, model_outputs) -> Tuple[List[List], List]:
        """
        post-process the word attributions to merge the sub-words tokens
        to words
        Args:
            model_outputs: word importance scores
        Returns:
            Tuple of reduced inputs and the smallest indices
        """
        attributions = model_outputs["attributions"][0]
        context_attributions = attributions["context_tokens"][0]
        question_attributions = attributions["question_tokens"][0]

        context_text = " ".join([word[1] for word in context_attributions])
        question_text = " ".join([word[1] for word in question_attributions])

        question_tokens = np.array([word[1] for word in question_attributions])
        question_attr = np.array([word[2] for word in question_attributions])
        smallest_indices = np.argsort(question_attr)[: self.top_k].tolist()

        reduced_instances_and_smallest: List[Tuple] = []
        while len(question_tokens) != 1:
            instance = deepcopy(question_tokens)

            # find smallest
            smallest = np.argmin(question_attr)
            question_attr = np.delete(question_attr, smallest)
            question_tokens = np.delete(question_tokens, smallest)

            # remove smallest
            inputs_before_smallest = instance[0:smallest]
            inputs_after_smallest = instance[smallest + 1 :]
            reduced_instance = np.append(inputs_before_smallest, inputs_after_smallest)

            reduced_instances_and_smallest.append(
                (" ".join(list(reduced_instance)), smallest)
            )
            # decrement top k
            self.top_k -= 1
            if self.top_k == 0:
                break

        reduced_questions = [entry[0] for entry in reduced_instances_and_smallest]
        prepared_inputs = [
            [q, c]
            for q, c in zip(
                [question_text] + reduced_questions,
                [context_text] * (len(reduced_questions) + 1),
            )
        ]

        return prepared_inputs, smallest_indices
