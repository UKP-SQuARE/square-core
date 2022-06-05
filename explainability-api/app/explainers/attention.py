import json
from typing import List

import torch
from transformers import (
    AutoTokenizer,
    BertAdapterModel,
    PreTrainedModel,
    PreTrainedTokenizer,
    logging
)

from base_explainer import BaseExplainer

logging.set_verbosity_error()


class AttnAttributions(BaseExplainer):
    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer
                 ):
        super().__init__(model=model, tokenizer=tokenizer)

    def interpret(self, inputs: List[List], top_k, mode: str = "context", output: str = "processed"):
        # get predicted answer
        model_kwargs = {"output_attentions": True}
        outputs, _ = self._predict(inputs, **model_kwargs)
        start_idx = torch.argmax(outputs[0])
        end_idx = torch.argmax(outputs[1])

        answer_start = torch.tensor([start_idx])
        answer_end = torch.tensor([end_idx])

        attn = outputs["attentions"][-1]
        weights = attn[:, :, 0, :].mean(1)
        attributions = weights.cpu().detach().numpy()[0]

        if output == "raw":
            return self.encode(inputs, add_special_tokens=True, return_tensors="pt"),\
                               attributions, answer_start, answer_end

        outputs = self.process_outputs(attributions=attributions, top_k=top_k, mode=mode)

        return json.dumps(outputs, indent=4)


if __name__ == '__main__':
    # model and tokenizer
    base_model = "bert-base-uncased"
    adapter_model = "AdapterHub/bert-base-uncased-pf-squad_v2"
    model = BertAdapterModel.from_pretrained(base_model)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    adapter_name = model.load_adapter(adapter_model, source="hf")
    model.active_adapters = adapter_name

    attn_attr = AttnAttributions(model, tokenizer)

    ques, cxt = "Who stars in The Matrix?", \
                "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring " \
                "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano. It " \
                "depicts a dystopian future in which reality as perceived by most humans is actually a simulated " \
                "reality called 'the Matrix': created by sentient machines to subdue the human population, while " \
                "their bodies' heat and electrical activity are used as an energy source. Computer programmer " \
                "'Neo' learns this truth and is drawn into a rebellion against the machines, which involves other " \
                "people who have been freed from the 'dream world.'"
    scores = attn_attr.interpret([[ques, cxt]], top_k=10, output="processed")
    print(scores)
