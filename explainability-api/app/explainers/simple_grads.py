import math
import json
import numpy as np
from typing import List, Dict
import torch
from transformers import (
    AutoTokenizer,
    BertAdapterModel,
    AutoModelWithHeads,
    PreTrainedModel,
    PreTrainedTokenizer,
    logging
)
from base_explainer import BaseExplainer


logging.set_verbosity_error()

torch.manual_seed(4)
torch.cuda.manual_seed(4)
np.random.seed(4)


class SimpleGradients(BaseExplainer):
    """
    class for the implementation of simple gradients' explanation method
    """
    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer
                 ):
        super().__init__(model=model, tokenizer=tokenizer)

    def interpret(self,
                  inputs: List[List],
                  top_k: int = 5,
                  mode: str = "all",
                  output: str = "processed"
                  ):
        """
        gets the word attributions
        """
        # get predicted answer
        outputs = self._predict(inputs)
        start_idx = torch.argmax(outputs[0])
        end_idx = torch.argmax(outputs[1])

        answer_start = torch.tensor([start_idx])
        answer_end = torch.tensor([end_idx])

        embeddings_list: List[torch.Tensor] = []
        # Hook used for saving embeddings
        handles: List = self._register_hooks(embeddings_list)
        try:
            grads = self.get_gradients(inputs, answer_start, answer_end)
        finally:
            for handle in handles:
                handle.remove()

        # Gradients come back in the reverse order that they were sent into the network
        embeddings_list.reverse()
        embeddings_list = [embedding.cpu().detach().numpy() for embedding in embeddings_list]
        # token_offsets.reverse()
        # embeddings_list = self._aggregate_token_embeddings(embeddings_list, token_offsets)
        instances_with_grads = dict()
        for key, grad in grads.items():
            # Get number at the end of every gradient key (they look like grad_input_[int],
            # we're getting this [int] part and subtracting 1 for zero-based indexing).
            # This is then used as an index into the reversed input array to match up the
            # gradient and its respective embedding.
            input_idx = int(key[-1]) - 1
            # The [0] here is undo-ing the batching that happens in get_gradients.
            emb_grad = np.sum(grad[0] * embeddings_list[input_idx][0], axis=1)
            norm = np.linalg.norm(emb_grad, ord=1)
            normalized_grad = [math.fabs(e) / norm for e in emb_grad]
            grads[key] = normalized_grad

        instances_with_grads["instance_" + str(1)] = grads

        if output == "raw":
            return self.encode(inputs, add_special_tokens=True, return_tensors="pt"),\
                   instances_with_grads["instance_1"]["grad_input_1"], answer_start, answer_end

        outputs = self.process_outputs(attributions=instances_with_grads["instance_1"]["grad_input_1"],
                                       top_k=top_k, mode=mode)

        return json.dumps(outputs, indent=4)


if __name__ == '__main__':
    # model and tokenizer
    # base_model = "bert-base-uncased"
    # adapter_model = "AdapterHub/bert-base-uncased-pf-squad_v2"
    # model = BertAdapterModel.from_pretrained(base_model)
    # tokenizer = AutoTokenizer.from_pretrained(base_model)
    # adapter_name = model.load_adapter(adapter_model, source="hf")
    # model.active_adapters = adapter_name

    model = AutoModelWithHeads.from_pretrained("roberta-base")
    tokenizer = AutoTokenizer.from_pretrained("roberta-base")
    adapter_name = model.load_adapter("AdapterHub/roberta-base-pf-squad", source="hf")
    model.active_adapters = adapter_name

    vanilla_grads = SimpleGradients(model, tokenizer)
    ques, cxt = "Who stars in The Matrix?", \
                "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring " \
                "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano. It " \
                "depicts a dystopian future in which reality as perceived by most humans is actually a simulated " \
                "reality called 'the Matrix': created by sentient machines to subdue the human population, while " \
                "their bodies' heat and electrical activity are used as an energy source. Computer programmer " \
                "'Neo' learns this truth and is drawn into a rebellion against the machines, which involves other " \
                "people who have been freed from the 'dream world.'"
    scores = vanilla_grads.interpret([[ques, cxt]], top_k=10, mode="context", output="processed")
    print(scores)
    # print(vanilla_grads.question_answering([[ques, cxt]]))
    # res = {'[CLS]': 0.26, 'who': 0.30,
    #        'wa': 0.30, '##cho': 0.55, '##wski': 0.15, '##s': 0.27, ',': 0.18,
    #        'starring': 4.62, 'ke': 0.80, '##anu': 5.60,
    #        'fish': 0.50, '##burn': 1.80, '##e': 1.50,
    #        'pan': 0.70, '##to': 0.20, '##lian': 0.30,
    #        '##o': 1.80}
    # x = process_outputs()
    # print(x)
