# This file is used for the Docker image to cache long-running setup for the tests,
# i.e., downloading finetuned Transformer models and so on.
# This way, adding new tests or even changing the server code does NOT trigger a new download during building
from starlette.config import environ
TRANSFORMERS_TESTING_CACHE = "./model_testing_cache"
environ["TRANSFORMERS_CACHE"] = TRANSFORMERS_TESTING_CACHE
environ["MODEL_NAME"] = "test"
environ["MODEL_TYPE"] = "test"
environ["DISABLE_GPU"] = "True"
environ["BATCH_SIZE"] = "1"
environ["RETURN_PLAINTEXT_ARRAYS"] = "True"

from square_model_inference.inference.transformer import Transformer
from square_model_inference.inference.adaptertransformer import AdapterTransformer
from square_model_inference.inference.sentencetransformer import SentenceTransformer

#Downloaded models:
TRANSFORMER_MODEL = "bert-base-uncased"
SENTENCE_MODEL = "paraphrase-albert-small-v2"

if __name__ == "__main__":
    bert_transformer = Transformer(TRANSFORMER_MODEL, "base", 1, True)
    adapter_transformer = AdapterTransformer(TRANSFORMER_MODEL, 1, True, TRANSFORMERS_TESTING_CACHE)
    sentence_transformer = SentenceTransformer(SENTENCE_MODEL)