from transformers.adapters import list_adapters
import torch
import collections
from transformers import AutoModel, AutoTokenizer


def _average_adapter_params(adapter_names, state_dict, proportions=None):
    """
    Average multiple adapter weights and return the averaged state_dict
    """
    if proportions is None:
        proportions = {
            a: torch.tensor(1 / len(adapter_names))
            for a in adapter_names
        }
    param_lst = collections.defaultdict(list)
    for k, p in state_dict.items():
        for name in adapter_names:
            if f"adapters.{name}." in k:
                rk = k.replace(f".{name}.", f".adapter.")
                param_lst[rk].append(p * proportions[name])
            if f"heads.{name}." in k:
                rk = k.replace(f"heads.{name}.", "head.")
                param_lst[rk].append(p * proportions[name])
    avg_dict = {
        k: torch.sum(torch.stack(vs, dim=0), dim=0)
        for k, vs in param_lst.items()
    }
    return avg_dict


if __name__ == '__main__':
    base_model = "bert-base-uncased"
    adapter_names = ["AdapterHub/bert-base-uncased-pf-squad_v2", "AdapterHub/bert-base-uncased-pf-squad"]
    # torch.load(adapter_names[0])
    # for path in adapter_names:
    #     model = AutoModel.from_pretrained(path)
    #     tokenizer = AutoTokenizer.from_pretrained(path)

    # load base model
    model = AutoModel.from_pretrained(base_model)
    state_dict = {}
    for name in adapter_names:
        model.load_adapter(name, load_as=name, source=None)
        # print(model)
        p_state_dict = model.state_dict()
        state_dict.update(p_state_dict)
    avg_dict = _average_adapter_params(adapter_names, state_dict)
    state_dict.update(avg_dict)

    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    print(f"{len(missing)} missing, {len(unexpected)} unexpected")
    print(f"missing: {missing}")
    print(f"unexpected: {unexpected}")
    missing = set(missing)
    missing_new = [
        k
        for k, p in model.named_parameters()
        if p.requires_grad and k in missing
    ]
    print(f"missing parameters with requires_grad: {missing_new}")
