import math
import json
import numpy as np
from transformers import (
    AutoTokenizer,
    BertAdapterModel,
    RobertaAdapterModel,
    PreTrainedModel,
    PreTrainedTokenizer,
    logging
)

import torch
from torch import backends
from torch.nn import Module, ModuleList
from typing import List, Tuple

from base_explainer import BaseExplainer


logging.set_verbosity_error()

torch.manual_seed(4)
torch.cuda.manual_seed(4)
np.random.seed(4)


class ScaledAttention(BaseExplainer):
    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer
                 ):
        super().__init__(model=model, tokenizer=tokenizer)

    def get_model_attentions(self) -> Module or ModuleList:
        """
        Get the model attention layer
        :return:
        """
        model_prefix = self.model.base_model_prefix
        model_base = getattr(self.model, model_prefix)
        model_enc = getattr(model_base, "encoder")
        # get attn weights from last layer
        attentions = model_enc.layer[-1].attention
        return attentions

    def _register_forward_hooks(self, attentions_list: List):
        """
        Register the model attentions during the forward pass
        :param attentions_list:
        :return:
        """

        def forward_hook(module, inputs, output):
            attentions_list.append(output[1][:, :, 0, :].mean(1).squeeze(0).clone().detach())

        handles = []
        attn_layer = self.get_model_attentions()
        handles.append(attn_layer.register_forward_hook(forward_hook))
        return handles

    def _register_attention_gradient_hooks(self, attn_grads: List):
        """
        Register the model gradients during the backward pass
        :param embedding_grads:
        :return:
        """
        def hook_layers(module, grad_in, grad_out):
            grads = grad_out[0]
            attn_grads.append(grads)

        hooks = []
        attentions = self.get_model_attentions()
        hooks.append(attentions.register_full_backward_hook(hook_layers))
        return hooks

    def get_gradients(self, inputs, answer_start, answer_end):
        """
        Compute model gradients
        :param inputs: list of question and context
        :param answer_start: answer span start
        :param answer_end: answer span end
        :return: dict of model gradients
        """
        attn_gradients: List[torch.Tensor] = []
        # print(answer_start, answer_end)

        original_param_name_to_requires_grad_dict = {}
        for param_name, param in self.model.named_parameters():
            original_param_name_to_requires_grad_dict[param_name] = param.requires_grad
            param.requires_grad = True

        hooks: List = self._register_attention_gradient_hooks(attn_gradients)
        with backends.cudnn.flags(enabled=False):
            encoded_inputs = self.encode(inputs, return_tensors="pt")
            encoded_inputs.to(self.device)
            outputs = self.model(
                **encoded_inputs,
                start_positions=answer_start.to(self.device),
                end_positions=answer_end.to(self.device),
                output_attentions=True
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
        for idx, grad in enumerate(attn_gradients):
            key = "grad_input_" + str(idx + 1)
            grad_dict[key] = grad.detach().cpu().numpy()

        # restore the original requires_grad values of the parameters
        for param_name, param in self.model.named_parameters():
            param.requires_grad = original_param_name_to_requires_grad_dict[param_name]
        # print(grad_dict)
        return grad_dict

    def interpret(self, inputs: List[List], top_k, mode: str = "context", output: str = "processed"):
        # get predicted answer
        outputs, _ = self._predict(inputs)
        start_idx = torch.argmax(outputs[0])
        end_idx = torch.argmax(outputs[1])

        answer_start = torch.tensor([start_idx])
        answer_end = torch.tensor([end_idx])

        attentions_list: List[torch.Tensor] = []
        # Hook used for saving embeddings
        handles: List = self._register_forward_hooks(attentions_list)
        try:
            grads = self.get_gradients(inputs, answer_start, answer_end)
            # print(grads["grad_input_1"][:, :, 0, :].mean(1))
        finally:
            for handle in handles:
                handle.remove()

        # Gradients come back in the reverse order that they were sent into the network
        attentions_list.reverse()
        attentions_list = [attn.cpu().detach().numpy() for attn in attentions_list]

        instances_with_grads = dict()
        for key, grad in grads.items():
            attn_grad = np.sum(grad[0], axis=1)
            norm = np.linalg.norm(attn_grad, ord=1)
            normalized_grad = [math.fabs(e) / norm for e in attn_grad]
            grads[key] = normalized_grad

        instances_with_grads["instance_" + str(1)] = grads

        if output == "raw":
            return self.encode(inputs, add_special_tokens=True, return_tensors="pt"),\
                   instances_with_grads["instance_1"]["grad_input_1"]*attentions_list[0], answer_start, answer_end

        outputs = self.process_outputs(attributions=list(instances_with_grads["instance_1"]["grad_input_1"]),
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

    model = RobertaAdapterModel.from_pretrained("roberta-base")
    tokenizer = AutoTokenizer.from_pretrained("roberta-base")
    adapter_name = model.load_adapter("AdapterHub/roberta-base-pf-squad", source="hf")
    model.active_adapters = adapter_name

    scale_attn = ScaledAttention(model, tokenizer)

    ques, cxt = "Who stars in The Matrix?", \
                "The Matrix is a 1999 science fiction action film written and directed by The Wachowskis, starring " \
                "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano. It " \
                "depicts a dystopian future in which reality as perceived by most humans is actually a simulated " \
                "reality called 'the Matrix': created by sentient machines to subdue the human population, while " \
                "their bodies' heat and electrical activity are used as an energy source. Computer programmer " \
                "'Neo' learns this truth and is drawn into a rebellion against the machines, which involves other " \
                "people who have been freed from the 'dream world.'"
    scores = scale_attn.interpret([[ques, cxt]], top_k=10, output="processed")
    print(scores)
