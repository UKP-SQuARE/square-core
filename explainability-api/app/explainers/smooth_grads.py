import numpy as np
from transformers import (
    AutoTokenizer,
    BertAdapterModel,
    PreTrainedModel,
    PreTrainedTokenizer,
    logging
)
import torch
from torch import backends
from torch.nn import Module, ModuleList
from typing import List, Dict, Tuple, Any
import math
import json

from base_explainer import BaseExplainer

logging.set_verbosity_error()

torch.manual_seed(4)
torch.cuda.manual_seed(4)
np.random.seed(4)


class SmoothGradients(BaseExplainer):
    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer
                 ):
        super().__init__(model=model, tokenizer=tokenizer)

        # hyperparams
        self.stdev = 0.01
        self.num_samples = 10

    def _register_forward_hook(self, stdev: float):
        """
        Forward hooks to get model embeddings with added noise
        """
        def forward_hook(module, inputs, output):
            # Random noise = N(0, stdev * (max-min))
            scale = output.detach().max() - output.detach().min()
            noise = torch.randn(output.shape, device=output.device) * stdev * scale

            # Add the random noise
            output.add_(noise)

        embedding_layer = self.get_model_embeddings()
        handle = embedding_layer.register_forward_hook(forward_hook)
        return handle

    def _smooth_grads(self, inputs) -> Tuple[Dict[str, np.ndarray], torch.Tensor, torch.Tensor]:

        outputs, _ = self._predict(inputs)
        start_idx = torch.argmax(outputs[0])
        end_idx = torch.argmax(outputs[1])
        answer_start = torch.tensor([start_idx])
        answer_end = torch.tensor([end_idx])

        total_gradients: Dict[str, Any] = {}
        for _ in range(self.num_samples):
            handle = self._register_forward_hook(self.stdev)
            try:
                grads = self.get_gradients(inputs, answer_start, answer_end)
            finally:
                handle.remove()

            # Sum gradients
            if total_gradients == {}:
                total_gradients = grads
            else:
                for key in grads.keys():
                    total_gradients[key] += grads[key]

        # Average the gradients
        for key in total_gradients.keys():
            total_gradients[key] /= self.num_samples

        return total_gradients, answer_start, answer_end

    def interpret(self, inputs: List[List], top_k: int, mode: str = "all", output: str = "processed"):
        # run smooth grad
        grads, answer_start, answer_end = self._smooth_grads(inputs)
        # normalize results
        instances_with_grads = dict()
        for key, grad in grads.items():
            # The [0] here is undo-ing the batching that happens in get_gradients.
            embedding_grad = np.sum(grad[0], axis=1)
            norm = np.linalg.norm(embedding_grad, ord=1)
            normalized_grad = np.array([math.fabs(e) / norm for e in embedding_grad])
            grads[key] = normalized_grad

        instances_with_grads["instance_" + str(1)] = grads
        if output == "raw":
            return self.encode(inputs, add_special_tokens=True, return_tensors="pt"), \
                   instances_with_grads["instance_1"]["grad_input_1"], answer_start, answer_end

        outputs = self.process_outputs(attributions=list(instances_with_grads["instance_1"]["grad_input_1"]),
                                       top_k=top_k, mode=mode)

        return json.dumps(outputs, indent=4)


if __name__ == '__main__':
    # model and tokenizer
    base_model = "bert-base-uncased"
    adapter_model = "AdapterHub/bert-base-uncased-pf-squad_v2"
    model = BertAdapterModel.from_pretrained(base_model)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    adapter_name = model.load_adapter(adapter_model, source="hf")
    model.active_adapters = adapter_name

    grads = SmoothGradients(model, tokenizer)

    ques, cxt = "Who stars in The Matrix?", \
                "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring " \
                "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano. It " \
                "depicts a dystopian future in which reality as perceived by most humans is actually a simulated " \
                "reality called 'the Matrix': created by sentient machines to subdue the human population, while " \
                "their bodies' heat and electrical activity are used as an energy source. Computer programmer " \
                "'Neo' learns this truth and is drawn into a rebellion against the machines, which involves other " \
                "people who have been freed from the 'dream world.'"
    scores = grads.interpret([[ques, cxt]], top_k=5)
    print(scores)
