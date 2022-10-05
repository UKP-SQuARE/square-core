import argparse
import logging
logger = logging.getLogger(__name__)
from starlette.config import environ


TRANSFORMERS_TESTING_CACHE = "./.model_testing_cache"
environ["TRANSFORMERS_CACHE"] = TRANSFORMERS_TESTING_CACHE
environ["MODEL_NAME"] = "test"
environ["MODEL_TYPE"] = "test"
environ["DISABLE_GPU"] = "True"
environ["BATCH_SIZE"] = "1"
environ["RETURN_PLAINTEXT_ARRAYS"] = "True"
environ["MAX_INPUT_SIZE"] = "100"

# Downloaded models:
TRANSFORMER_MODEL = "bert-base-uncased"
TRANSFORMER_MODEL_ROBERTA= "roberta-base"
SENTENCE_MODEL = "paraphrase-albert-small-v2"
ONNX_MODEL = "bert-base-uncased"

if __name__ == "__main__":
    # We pre-download all models needed for the tests.
    # We have to be careful to NOT import anything from square_model_inference because this script runs in the Dockerfile
    # BEFORE any other of our code is copied (so that we do not have to re-download after every code change).
    device = "cpu"

    parser = argparse.ArgumentParser(description="indicate the pre-downloaded model")

    parser.add_argument("--transformer",  help="transformer based model",action="store_true")
    parser.add_argument("--sentence_transformer",  help="sentence transformer based model",action="store_true")
    # parser.add_argument("y", type=int, help="the exponent")

    args = parser.parse_args()
    if args.transformer == True:
        from transformers import AutoTokenizer, list_adapters
        from transformers.adapters import AutoAdapterModel
        # Pre-download Huggingface model for tests
        _ = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL)
        model = AutoAdapterModel.from_pretrained(TRANSFORMER_MODEL).to(device)

        _ = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL_ROBERTA)
        model = AutoAdapterModel.from_pretrained(TRANSFORMER_MODEL).to(device)

        # Pre-download adapters
        # logger.info("Loading all available adapters")
        # adapter_infos = [info for info in list_adapters(source="ah") if info.model_name==TRANSFORMER_MODEL]
        # adapters = set(f"{adapter_info.task}/{adapter_info.subtask}@{adapter_info.username}" for adapter_info in adapter_infos)
        adapters = set(["nli/rte@ukp", "ner/conll2003@ukp", "sts/sts-b@ukp", "qa/squad2@ukp"])
        for adapter in adapters:
            logger.debug(f"Loading adapter {adapter}")
            try:
                model.load_adapter(adapter, load_as=adapter, with_head=True, cache_dir=TRANSFORMERS_TESTING_CACHE)
            except RuntimeError as e:
                if "Error(s) in loading state_dict" in e.args[0]:
                    logger.debug(f"Could not load {adapter} due to missing label_ids in config resulting in exception:\n{e.args[0]}")
                else:
                    raise(e)
    if args.sentence_transformer == True:
        from sentence_transformers import SentenceTransformer
        # Pre-download sentence-transformer models for tests
        _ = SentenceTransformer(model_name_or_path=SENTENCE_MODEL, device=device)
