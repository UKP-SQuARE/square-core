# This is a stand-alone script that does not require additional code (except the imported packages).
# We copy-pasted code from Model API and removing some not needed stuff for this.
import argparse
import json
import logging
import os
import pickle
import queue
import time
from dataclasses import dataclass
from typing import List, Union

import h5py
import numpy as np
import torch
import torch.multiprocessing as mp

# Conditionally load adapter or sentence-transformer later to simplify installation
# from sentence_transformers import SentenceTransformer as SentenceTransformerModel
import transformers
from transformers import AutoModel, AutoTokenizer  # , AutoModelWithHeads


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(processName)s-%(levelname)s-%(asctime)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@dataclass
class PredictionRequest:
    """
    Prediction request containing the input, pre-processing parameters, parameters for the model forward pass,
     the task with task-specific parameters, and parameters for any post-processing
    """

    input: Union[List[str], List[List[str]], dict]
    preprocessing_kwargs: dict
    model_kwargs: dict
    task_kwargs: dict


class SentenceTransformer:
    """
    The class for all sentence-transformers models
    """

    def __init__(self, model_name, batch_size, disable_gpu):
        """
        Initialize the SentenceTransformer
        :param model_name: the sentence-transformer model name (https://sbert.net/docs/pretrained_models.html)
        :param batch_size: batch size used for inference
        :param disable_gpu: do not move model to GPU even if CUDA is available
        """
        self._load_model(model_name, disable_gpu)
        self.batch_size = batch_size

    def to(self, device):
        self.model.to(device)

    def _load_model(self, model_name, disable_gpu):
        """
        Load the Transformer model model_name and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or disable_gpu is true.
        """
        import sentence_transformers

        logger.debug(f"Loading model {model_name}")
        device = "cuda" if torch.cuda.is_available() and not disable_gpu else "cpu"
        model = sentence_transformers.SentenceTransformer(model_name_or_path=model_name, device=device)
        logger.info(f"Model {model_name} loaded on {device}")
        self.model = model

    def embedding(self, request):
        embeddings = self.model.encode(
            request.input,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_tensor=True,
        )
        return embeddings


class Transformer:
    """
    The class for all Huggingface transformer-based models
    """

    SUPPORTED_EMBEDDING_MODES = ["mean", "max", "cls", "token"]

    def __init__(self, model_name, batch_size, disable_gpu):
        """
        Initialize the Transformer
        :param model_name: the Huggingface model name
        :param batch_size: batch size used for inference
        :param disable_gpu: do not move model to GPU even if CUDA is available
        """
        self._load_model(AutoModel, model_name, disable_gpu)
        self.batch_size = batch_size

    def to(self, device):
        self.model.to(device)

    def _load_model(self, model_cls, model_name, disable_gpu):
        """
        Load the Transformer model model_name and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or disable_gpu is true.
        """
        logger.debug(f"Loading model {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Check if GPU is available
        device = "cuda" if torch.cuda.is_available() and not disable_gpu else "cpu"
        model = model_cls.from_pretrained(model_name).to(device)
        logger.info(f"Model {model_name} loaded on {device}")

        self.model = model
        self.tokenizer = tokenizer

    def _ensure_tensor_on_device(self, **inputs):
        """
        Ensure PyTorch tensors are on the specified device.

        Args:
            inputs (keyword arguments that should be :obj:`torch.Tensor`): The tensors to place on :obj:`self.device`.

        Return:
            :obj:`Dict[str, torch.Tensor]`: The same as :obj:`inputs` but on the proper device.
        """
        return {name: tensor.to(self.model.device) for name, tensor in inputs.items()}

    def _predict(self, request, output_features=False):
        """
        Inference on the input.
        :param request: the request with the input and optional kwargs
        :param output_features: return the features of the input.
        Necessary if, e.g., attention mask is needed for post-processing.
        :return: The model outputs and optionally the input features
        """
        all_predictions = []
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get("padding", True)
        request.preprocessing_kwargs["truncation"] = request.preprocessing_kwargs.get("truncation", True)
        features = self.tokenizer(request.input, return_tensors="pt", **request.preprocessing_kwargs)
        for start_idx in range(0, len(request.input), self.batch_size):
            with torch.no_grad():
                input_features = {k: features[k][start_idx : start_idx + self.batch_size] for k in features.keys()}
                input_features = self._ensure_tensor_on_device(**input_features)
                predictions = self.model(**input_features, **request.model_kwargs)
                all_predictions.append(predictions)
        keys = all_predictions[0].keys()
        final_prediction = {}
        for key in keys:
            # HuggingFace outputs for 'attentions' and more is returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values' which is only relevant for generation.
            # Generation should NOT use this function
            if isinstance(all_predictions[0][key], tuple):
                tuple_of_lists = list(zip(*[[p.cpu() for p in tpl[key]] for tpl in all_predictions]))
                final_prediction[key] = tuple(torch.cat(l) for l in tuple_of_lists)
            else:
                final_prediction[key] = torch.cat([p[key].cpu() for p in all_predictions])
        if output_features:
            return final_prediction, features
        return final_prediction

    def embedding(self, request):
        request.model_kwargs["output_hidden_states"] = True
        predictions, features = self._predict(request, output_features=True)
        # We remove hidden_states from predictions!
        hidden_state = predictions.pop("hidden_states")[-1]
        attention_mask = features["attention_mask"]

        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")

        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(
                f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}"
            )

        if embedding_mode == "cls":
            emb = hidden_state[:, 0, :]
        # copied from sentence-transformers pooling
        elif embedding_mode == "max":
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            hidden_state[input_mask_expanded == 0] = -1e9  # Set padding tokens to large negative value
            emb = torch.max(hidden_state, 1)[0]
        # copied from sentence-transformers pooling
        elif embedding_mode == "mean":
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            sum_embeddings = torch.sum(hidden_state * input_mask_expanded, 1)
            sum_mask = input_mask_expanded.sum(1)
            emb = sum_embeddings / sum_mask
        elif embedding_mode == "token":
            emb = hidden_state
        return emb


class AdapterTransformer(Transformer):
    """
    The class for all adapter-based models using the adapter-transformers package
    """

    def __init__(self, model_name, batch_size, disable_gpu, transformers_cache, adapter_name):
        """
        Initialize the Adapter with its underlying Transformer and pre-load all available adapters from adapterhub.ml
        :param model_name: the Huggingface model name
        :param batch_size: batch size used for inference
        :param disable_gpu: do not move model to GPU even if CUDA is available
        :param transformers_cache: Should be same as TRANSFORMERS_CACHE env variable.
        This folder will be used to store the adapters
        """
        self._load_model(transformers.AutoModelWithHeads, model_name, disable_gpu)
        self.model.load_adapter(adapter_name, load_as=adapter_name, cache_dir=transformers_cache)
        self.model.to(self.model.device)
        self.model.set_active_adapters(adapter_name)
        self.batch_size = batch_size


def read_batch(file_pointer, batch_size):
    i = 0
    lines = []
    finished = False
    while i < batch_size:
        line = file_pointer.readline().strip()
        # empty string -> file finished
        if not line:
            finished = True
            break
        else:
            lines.append(line)
        i += 1
    return lines, finished


def encode(args):
    transformers_cache = args.transformers_cache
    os.environ["TRANSFORMERS_CACHE"] = transformers_cache
    model_name = args.model_name
    model_type = args.model_type
    batch_size = args.batch_size
    chunk_size = args.chunk_size
    input_file = args.input_file
    output_file = os.path.splitext(args.output_file)[0]  # Remove .pkl from name
    adapter_name = args.adapter_name

    if model_type == "sentence-transformer":
        model = SentenceTransformer(model_name, batch_size, False)
    elif model_type == "transformer":
        model = Transformer(model_name, batch_size, False)
    elif model_type == "adapter":
        model = AdapterTransformer(model_name, batch_size, False, transformers_cache, adapter_name)

    logger.info(f"Reading input from {input_file}")
    if os.path.dirname(output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, "r", encoding="utf-8") as f_in:
        # We do not know how large the input file is so we read it batch-wise for memory safety reasons
        finished_reading = False
        total_processed_lines = 0
        chunk_idx = 0
        current_processed_lines = 0
        current_output = {"ids": [], "embeddings": []}
        while not finished_reading:
            lines, finished_reading = read_batch(f_in, batch_size)
            if lines:
                lines = [json.loads(line) for line in lines]
                texts = [line["text"] for line in lines]
                ids = [line["id"] for line in lines]

                input = PredictionRequest(
                    input=texts,
                    preprocessing_kwargs={},
                    model_kwargs={},
                    task_kwargs={"embedding_mode": "mean"},
                )
                embeddings = model.embedding(input)
                embeddings = embeddings.cpu().numpy()
                if args.float16:
                    embeddings = embeddings.astype("float16")

                current_output["ids"].extend(ids)
                current_output["embeddings"].append(embeddings)

            total_processed_lines += len(lines)
            current_processed_lines += len(lines)

            if current_processed_lines >= chunk_size or finished_reading:
                logger.info(f"Processed {total_processed_lines} lines ({chunk_idx+1} chunks)")

                current_output["embeddings"] = np.concatenate(current_output["embeddings"])

                if args.hdf5:
                    chunk_output_file = f"{output_file}_{chunk_idx}.h5"
                    with h5py.File(chunk_output_file, "w") as out_f:
                        logger.info(f"Writing chunk in {chunk_output_file}")
                        if args.hdf5_gzip_level < 0:
                            out_f.create_dataset("ids", data=np.array(current_output["ids"], dtype="S"))
                            out_f.create_dataset("embeddings", data=current_output["embeddings"])
                        else:
                            out_f.create_dataset(
                                "ids",
                                data=np.array(current_output["ids"], dtype="S"),
                                compression="gzip",
                                compression_opts=min(args.hdf5_gzip_level, 9),
                            )
                            out_f.create_dataset(
                                "embeddings",
                                data=current_output["embeddings"],
                                compression="gzip",
                                compression_opts=min(args.hdf5_gzip_level, 9),
                            )
                else:
                    chunk_output_file = f"{output_file}_{chunk_idx}.pkl"
                    with open(chunk_output_file, "wb") as out_f:
                        logger.info(f"Writing chunk in {chunk_output_file}")
                        pickle.dump(current_output, out_f)
                current_processed_lines = 0
                current_output = {"ids": [], "embeddings": []}
                chunk_idx += 1


def _read_process(input_file, batch_size, input_queue):
    logger.info(f"Reading input from {input_file}")
    with open(input_file, "r", encoding="utf-8") as f_in:
        # We do not know how large the input file is so we read it batch-wise for memory safety reasons
        finished_reading = False
        while not finished_reading:
            lines, finished_reading = read_batch(f_in, batch_size)
            if lines:
                lines = [json.loads(line) for line in lines]
                texts = [line["text"] for line in lines]
                ids = [line["id"] for line in lines]

                input = PredictionRequest(
                    input=texts,
                    preprocessing_kwargs={},
                    model_kwargs={},
                    task_kwargs={"embedding_mode": "mean"},
                )
                input_queue.put((input, ids), block=True)


def _encode_process(model, device, float16, input_queue, output_queue):
    logger.info(f"Moving model to {device}")
    model.to(device)
    while True:
        try:
            input, ids = input_queue.get()
            embeddings = model.embedding(input)
            embeddings = embeddings.cpu().numpy()
            if float16:
                embeddings = embeddings.astype("float16")
            output_queue.put((embeddings, ids))
        except queue.Empty:
            break


def _write_process(output_file, chunk_size, args, output_queue):
    chunk_idx = 0
    current_processed_lines = 0
    total_processed_lines = 0
    current_output = {"ids": [], "embeddings": []}
    while True:
        try:
            # We do not know when we are done writing. Instead we wait 60s and if we get nothing new, we assume we are done.
            # i.e., after the timeout, queue.Empty exception is triggered and we write the remaining output and finish
            embeddings, ids = output_queue.get(timeout=60)
            current_output["ids"].extend(ids)
            current_output["embeddings"].append(embeddings)

            total_processed_lines += len(ids)
            current_processed_lines += len(ids)

            if current_processed_lines >= chunk_size:
                logger.info(f"Processed {total_processed_lines} lines ({chunk_idx+1} chunks)")

                current_output["embeddings"] = np.concatenate(current_output["embeddings"])

                if args.hdf5:
                    chunk_output_file = f"{output_file}_{chunk_idx}.h5"
                    with h5py.File(chunk_output_file, "w") as out_f:
                        logger.info(f"Writing chunk in {chunk_output_file}")
                        if args.hdf5_gzip_level < 0:
                            out_f.create_dataset("ids", data=np.array(current_output["ids"], dtype="S"))
                            out_f.create_dataset("embeddings", data=current_output["embeddings"])
                        else:
                            out_f.create_dataset(
                                "ids",
                                data=np.array(current_output["ids"], dtype="S"),
                                compression="gzip",
                                compression_opts=min(args.hdf5_gzip_level, 9),
                            )
                            out_f.create_dataset(
                                "embeddings",
                                data=current_output["embeddings"],
                                compression="gzip",
                                compression_opts=min(args.hdf5_gzip_level, 9),
                            )
                else:
                    chunk_output_file = f"{output_file}_{chunk_idx}.pkl"
                    with open(chunk_output_file, "wb") as out_f:
                        logger.info(f"Writing chunk in {chunk_output_file}")
                        pickle.dump(current_output, out_f)
                current_processed_lines = 0
                current_output = {"ids": [], "embeddings": []}
                chunk_idx += 1
        except queue.Empty:
            logger.info(f"Processed {total_processed_lines} lines ({chunk_idx+1} chunks)")
            current_output["embeddings"] = np.concatenate(current_output["embeddings"])
            if args.hdf5:
                chunk_output_file = f"{output_file}_{chunk_idx}.h5"
                with h5py.File(chunk_output_file, "w") as out_f:
                    logger.info(f"Writing chunk in {chunk_output_file}")
                    if args.hdf5_gzip_level < 0:
                        out_f.create_dataset("ids", data=np.array(current_output["ids"], dtype="S"))
                        out_f.create_dataset("embeddings", data=current_output["embeddings"])
                    else:
                        out_f.create_dataset(
                            "ids",
                            data=np.array(current_output["ids"], dtype="S"),
                            compression="gzip",
                            compression_opts=min(args.hdf5_gzip_level, 9),
                        )
                        out_f.create_dataset(
                            "embeddings",
                            data=current_output["embeddings"],
                            compression="gzip",
                            compression_opts=min(args.hdf5_gzip_level, 9),
                        )
            else:
                chunk_output_file = f"{output_file}_{chunk_idx}.pkl"
                with open(chunk_output_file, "wb") as out_f:
                    logger.info(f"Writing chunk in {chunk_output_file}")
                    pickle.dump(current_output, out_f)
            break


def encode_multiprocess(args):
    transformers_cache = args.transformers_cache
    os.environ["TRANSFORMERS_CACHE"] = transformers_cache
    model_name = args.model_name
    model_type = args.model_type
    batch_size = args.batch_size
    chunk_size = args.chunk_size
    input_file = args.input_file
    output_file = os.path.splitext(args.output_file)[0]  # Remove file extension from name
    adapter_name = args.adapter_name
    devices = args.gpus.split(",")

    ctx = mp.get_context("spawn")

    if model_type == "sentence-transformer":
        model = SentenceTransformer(model_name, batch_size, True)
    elif model_type == "transformer":
        model = Transformer(model_name, batch_size, True)
    elif model_type == "adapter":
        model = AdapterTransformer(model_name, batch_size, True, transformers_cache, adapter_name)

    if os.path.dirname(output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    input_queue = ctx.Queue(maxsize=2 * len(devices))
    output_queue = ctx.Queue()

    read_p = ctx.Process(target=_read_process, args=(input_file, batch_size, input_queue), daemon=True)
    read_p.start()
    write_p = ctx.Process(
        target=_write_process,
        args=(output_file, chunk_size, args, output_queue),
        daemon=True,
    )
    write_p.start()
    for cuda_id in devices:
        p = ctx.Process(
            target=_encode_process,
            args=(model, cuda_id, args.float16, input_queue, output_queue),
            daemon=True,
        )
        p.start()

    write_p.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transformers_cache",
        help="Cache folder where model files will be downloaded into and loaded from",
    )
    parser.add_argument(
        "--model_name",
        help="Model name, i.e., name used in transformers oder sentence-transformers to load the pre-trained model",
    )
    parser.add_argument(
        "--model_type",
        help="Model type, one of 'adapter', 'transformer', 'sentence-transformer'",
    )
    parser.add_argument("--batch_size", type=int, help="Batch size used for encoding")
    parser.add_argument(
        "--chunk_size",
        type=int,
        help="Chunk size used for writing out embeddings. "
        "ATTENTION: This value will be set to the first value satisfying: true_chunk_size mod batch_size == 0"
        "Each output file contains chunk_size embeddings "
        "(except the last one if len(input) mod chunk_size != 0)",
    )
    parser.add_argument(
        "--input_file",
        help="Input .jsonl file. Each line is a dict object: {'id': 'xxx', 'text': 'abc...'}",
    )
    parser.add_argument(
        "--output_file",
        help="Output .pkl/.h5 file. A chunk index will be inserted between the name and extension: e.g. 'path/to/name_chunkidx.pkl' ."
        "Format: {'ids': List[str], 'embeddings': ndarray}. "
        "Note for hdf5, use f['ids'].asstr() to load ids as string because default is binary.",
    )
    parser.add_argument(
        "--adapter_name",
        help="For model_type=adapter, the name of the adapter that should be loaded",
    )
    parser.add_argument("--hdf5", action="store_true", help="Save output with hdf5 instead of pickle")
    parser.add_argument(
        "--hdf5-gzip-level",
        type=int,
        default=4,
        help="GZIP compression level for HDF5 in range 0-9, default 4 (bigger is more compressed). "
        "Set to negative value to disable compression."
        "Only used when --hdf5 is also set.",
    )
    parser.add_argument("--float16", action="store_true", help="Save embeddings as float16")
    parser.add_argument(
        "--gpus",
        help="Set this value to use multiprocessing."
        "Comma-separated list of devices (e.g., cuda:0,cuda:1) for multi-GPU processing."
        "Reading, writing and each GPU is assigned its own process."
        "Can also be used with only one device to use the multiprocessing for reading/ writing of outputs but this is not necessarily faster with one GPU.",
    )
    args = parser.parse_args()

    start_time = time.time()
    if not args.gpus:
        encode(args)
    else:
        encode_multiprocess(args)
    end_time = time.time()
    logger.info(f"Finished encoding in {end_time-start_time}s")
