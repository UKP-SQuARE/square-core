from pydantic import BaseModel


class ModelStatistics(BaseModel):
    model_type: str # the model type e.g. transformer, onnx, adapter
    model_name: str # the model e.g. bert-base-cased
    batch_size: int # the batch size for the model
    max_input: int
    model_class: str # for transformers which model class this is e.g. base
    disable_gpu: bool
