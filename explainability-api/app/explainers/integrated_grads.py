import math
import json
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

from transformers import (
    AutoTokenizer,
    BertAdapterModel,
    PreTrainedModel,
    PreTrainedTokenizer,
    logging
)

from base_explainer import BaseExplainer

import torch

logging.set_verbosity_error()

torch.manual_seed(4)
torch.cuda.manual_seed(4)
np.random.seed(4)


class IntegratedGradients(BaseExplainer):
    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer
                 ):
        super().__init__(model=model, tokenizer=tokenizer)

    def _register_hooks(self, embeddings_list: List,  alpha: int):

        def forward_hook(module, inputs, output):
            # Save the input for later use. Only do so on first call.
            if alpha == 0:
                embeddings_list.append(output.squeeze(0).clone().detach())
            # Scale the embedding by alpha
            output.mul_(alpha)

        handles = []
        embedding_layer = self.get_model_embeddings()
        handles.append(embedding_layer.register_forward_hook(forward_hook))
        return handles

    def _integrate_gradients(self, inputs: List[List]) -> Tuple[Dict[str, np.ndarray], torch.Tensor, torch.Tensor]:
        """
        Returns:
             integrated gradients for the given [`Instance`]
        """
        ig_grads: Dict[str, Any] = {}

        # List of Embedding inputs
        embeddings_list: List[torch.Tensor] = []

        # answer prediction
        outputs, _ = self._predict(inputs)
        start_idx = torch.argmax(outputs[0])
        end_idx = torch.argmax(outputs[1])
        answer_start = torch.tensor([start_idx])
        answer_end = torch.tensor([end_idx])

        # Use 10 terms in the summation approximation of the integral in integrated grad
        steps = 10
        # Exclude the endpoint because we do a left point integral approximation
        for alpha in np.linspace(0, 1.0, num=steps, endpoint=False):
            handles = []
            # Hook for modifying embedding value
            handles = self._register_hooks(embeddings_list, alpha)

            try:
                grads = self.get_gradients(inputs, answer_start, answer_end)
            finally:
                for handle in handles:
                    handle.remove()

            # Running sum of gradients
            if ig_grads == {}:
                ig_grads = grads
            else:
                for key in grads.keys():
                    ig_grads[key] += grads[key]

        # Average of each gradient term
        for key in ig_grads.keys():
            ig_grads[key] /= steps

        # Gradients come back in the reverse order that they were sent into the network
        embeddings_list.reverse()
        embeddings_list = [embedding.cpu().detach().numpy() for embedding in embeddings_list]
        # Element-wise multiply average gradient by the input
        for idx, input_embedding in enumerate(embeddings_list):
            # print(idx, input_embedding)
            key = "grad_input_" + str(idx + 1)
            ig_grads[key] *= input_embedding

        return ig_grads, answer_start, answer_end

    def interpret(self, inputs: List[List], top_k: int, mode: str = "context", output: str = "processed"):
        # run integrated grad
        grads, answer_start, answer_end = self._integrate_gradients(inputs)
        # normalize results
        instances_with_grads = dict()
        for key, grad in grads.items():
            # The [0] here is undo-ing the batching that happens in get_gradients.
            embedding_grad = np.sum(grad[0], axis=1)
            norm = np.linalg.norm(embedding_grad, ord=1)
            normalized_grad = np.array([math.fabs(e) / norm for e in embedding_grad])
            grads[key] = normalized_grad

        instances_with_grads["instance_" + str(1)] = grads
        # print(type(instances_with_grads["instance_1"]["grad_input_1"]))

        if output == "raw":
            return self.encode(inputs, add_special_tokens=True, return_tensors="pt"), \
                   instances_with_grads["instance_1"]["grad_input_1"], answer_start, answer_end

        outputs = self.process_outputs(attributions=list(instances_with_grads["instance_1"]["grad_input_1"]),
                                       top_k=top_k, mode=mode)

        return json.dumps(outputs, indent=4)


if __name__ == '__main__':
    base_model = "bert-base-uncased"
    adapter_model = "AdapterHub/bert-base-uncased-pf-squad_v2"
    model = BertAdapterModel.from_pretrained(base_model)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    adapter_name = model.load_adapter(adapter_model, source="hf")
    model.active_adapters = adapter_name

    grads = IntegratedGradients(model, tokenizer)

    ques, cxt = "Who stars in The Matrix?", \
                "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring " \
                "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano. It " \
                "depicts a dystopian future in which reality as perceived by most humans is actually a simulated " \
                "reality called 'the Matrix': created by sentient machines to subdue the human population, while " \
                "their bodies' heat and electrical activity are used as an energy source. Computer programmer " \
                "'Neo' learns this truth and is drawn into a rebellion against the machines, which involves other " \
                "people who have been freed from the 'dream world.'"
    scores = grads.interpret([[ques, cxt]], top_k=10)
    print(scores)
