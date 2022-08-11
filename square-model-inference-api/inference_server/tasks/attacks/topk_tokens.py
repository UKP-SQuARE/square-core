from typing import List, Dict, Tuple
from copy import deepcopy
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TopkTokens:
    def __init__(
        self, top_k,
    ):
        self.top_k = top_k

    def choose_topk(self, model_outputs) -> Tuple[List[List], List]:
        """
        selects topk tokens from the context
        Args:
            model_outputs: word importance scores
        Returns:
            Tuple of reduced inputs and the largest indices
        """

        attributions = model_outputs["attributions"][0]
        context_attributions = attributions["context_tokens"][0]
        question_attributions = attributions["question_tokens"][0]

        context_text = " ".join([word[1] for word in context_attributions])
        question_text = " ".join([word[1] for word in question_attributions])

        context_tokens = np.array([word[1] for word in context_attributions])
        context_attr = np.array([word[2] for word in context_attributions])
        topk_indices = np.argsort(context_attr)[::-1][: self.top_k].tolist()

        reduced_instances_and_smallest: List = []
        while len(context_tokens) != 1:
            instance = deepcopy(context_tokens)

            # remove smallest
            smallest = np.argmin(context_attr)
            context_attr = np.delete(context_attr, smallest)
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
        return prepared_inputs, topk_indices
