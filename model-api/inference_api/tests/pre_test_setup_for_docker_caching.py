import argparse
import logging
import os


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


def create_test_model_path(model_type: str):
    """
    Create a mini untrained bert model to run the tests.It will create the model and config in local_dir
    Args:
        model_type: transformer or sentence-transformer
    """

    # small vocab for model
    vocab = [
        "[PAD]",
        "[UNK]",
        "[CLS]",
        "[SEP]",
        "[MASK]",
        "the",
        "of",
        "and",
        "in",
        "to",
        "was",
        "he",
    ]
    local_dir = os.getenv("TEST_MODEL_PATH", "./model4test")

    if not os.path.exists(local_dir):
        os.mkdir(local_dir)
    vocab_file = os.path.join(local_dir, "vocab.txt")
    with open(vocab_file, "w") as f:
        f.write("\n".join(vocab))
    config = BertConfig(
        vocab_size=10,
        hidden_size=768,
        num_attention_heads=1,
        num_hidden_layers=2,
        intermediate_size=2,
        max_position_embeddings=512,
    )
    # print(config)
    config.save_pretrained(save_directory=local_dir)
    model = BertModel(config)
    tokenizer = BertTokenizer(vocab_file=vocab_file)

    if model_type == "transformer":
        tokenizer.save_pretrained(local_dir)
        model.save_pretrained(local_dir)
    if model_type == "sentence-transformer":
        # the way to create sentence-bert is different.

        tokenizer.save_pretrained(local_dir)
        model.save_pretrained(local_dir)
        word_embedding_model = models.Transformer(local_dir)

        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        smodel = SentenceTransformer(modules=[word_embedding_model, pooling_model])
        smodel.save(local_dir)

    return local_dir


################### Models used for testing ###################
# TRANSFORMER_MODEL = "bert-base-uncased"
# TRANSFORMER_MODEL =create_test_model_path("transformer")
# TRANSFORMER_MODEL_ROBERTA= "roberta-base"
# SENTENCE_MODEL = "paraphrase-albert-small-v2"
# -------------------------------------------------------------


ONNX_MODEL = "bert-base-uncased"


if __name__ == "__main__":
    # We pre-download all models needed for the tests.
    # We have to be careful to NOT import anything from square_model_inference because this script runs in the Dockerfile
    # BEFORE any other of our code is copied (so that we do not have to re-download after every code change).
    device = "cpu"

    parser = argparse.ArgumentParser(description="indicate the pre-downloaded model")

    parser.add_argument("--transformer", help="transformer based model", action="store_true")
    parser.add_argument(
        "--sentence_transformer",
        help="sentence transformer based model",
        action="store_true",
    )
    # parser.add_argument("y", type=int, help="the exponent")

    args = parser.parse_args()
    if args.transformer:

        from transformers import AutoTokenizer, BertConfig, BertModel, BertTokenizer
        from transformers.adapters import BertAdapterModel

        TRANSFORMER_MODEL = create_test_model_path("transformer")

        # Pre-download Huggingface model for tests

        _ = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL)
        model = BertAdapterModel.from_pretrained(TRANSFORMER_MODEL).to(device)

        adapters = set(["nli/rte@ukp", "ner/conll2003@ukp", "sts/sts-b@ukp", "qa/squad2@ukp"])
        for adapter in adapters:
            logger.debug(f"Loading adapter {adapter}")
            try:
                model.load_adapter(
                    adapter,
                    model_name="bert-base-uncased",
                    load_as=adapter,
                    with_head=True,
                    cache_dir=TRANSFORMERS_TESTING_CACHE,
                )
            except RuntimeError as e:
                if "Error(s) in loading state_dict" in e.args[0]:
                    logger.debug(
                        f"Could not load {adapter} due to missing label_ids in config resulting in exception:\n{e.args[0]}"
                    )
                else:
                    raise (e)

    if args.sentence_transformer:
        from sentence_transformers import SentenceTransformer, models
        from transformers import BertConfig, BertModel, BertTokenizer

        SENTENCE_MODEL = create_test_model_path("sentence-transformer")
