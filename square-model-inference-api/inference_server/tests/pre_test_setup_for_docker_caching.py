# This file is used for the Docker image to cache long-running setup for the tests,
# i.e., downloading finetuned Transformer models and so on.
# This way, adding new tests or even changing the server code does NOT trigger a new download during building
import json

from sentence_transformers import SentenceTransformer
from starlette.config import environ
from transformers import AutoTokenizer, AutoModelWithHeads
from loguru import logger
from transformers.adapter_utils import download_cached, ADAPTER_HUB_INDEX_FILE

TRANSFORMERS_TESTING_CACHE = "./.model_testing_cache"
environ["TRANSFORMERS_CACHE"] = TRANSFORMERS_TESTING_CACHE
environ["MODEL_NAME"] = "test"
environ["MODEL_TYPE"] = "test"
environ["DISABLE_GPU"] = "True"
environ["BATCH_SIZE"] = "1"
environ["RETURN_PLAINTEXT_ARRAYS"] = "True"

# Downloaded models:
TRANSFORMER_MODEL = "bert-base-uncased"
SENTENCE_MODEL = "paraphrase-albert-small-v2"

if __name__ == "__main__":
    # We pre-download all models needed for the tests.
    # We have to be careful to NOT import anything from square_model_inference because this script runs in the Dockerfile
    # BEFORE any other of our code is copied (so that we do not have to re-download after every code change).
    device = "cpu"

    # Pre-download Huggingface model for tests
    _ = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL)
    model = AutoModelWithHeads.from_pretrained(TRANSFORMER_MODEL).to(device)

    # Pre-download adapters
    logger.warning("UPDATE with https://github.com/Adapter-Hub/adapter-transformers/pull/193")
    index_file = download_cached(ADAPTER_HUB_INDEX_FILE.format(TRANSFORMER_MODEL))
    adapter_index = json.load(open(index_file))
    adapters = set()
    for task, datasets in adapter_index.items():
        for dataset in datasets.keys():
            for key in datasets[dataset].keys():
                if key != "default":
                    for org in datasets[dataset][key]["versions"].keys():
                        adapters.add(f"{task}/{dataset}@{org}")
    for adapter in adapters:
        logger.debug(f"Loading adapter {adapter}")
        model.load_adapter(adapter, load_as=adapter, with_head=True, cache_dir=TRANSFORMERS_TESTING_CACHE)

    # Pre-download sentence-transformer models for tests
    _ = SentenceTransformer(model_name_or_path=SENTENCE_MODEL, device=device)
