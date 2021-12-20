import argparse
import glob
import logging
import os
import pickle

import faiss
import h5py
import numpy as np


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


def _read_file(file_path):
    if file_path.endswith(".h5"):
        logger.info("Reading h5 file: %s", file_path)
        with h5py.File(file_path, "r") as f:
            return f["ids"][:].tolist(), f["embeddings"][:]
    elif file_path.endswith(".pkl"):
        logger.info("Reading pkl file: %s", file_path)
        with open(file_path, "rb") as f:
            data = pickle.load(f)
            return data["ids"], data["embeddings"]
    else:
        raise ValueError(f"Unknown file type: {file_path}")


def _create_index(embeds_for_training, index):
    # Create and train the index
    embeds_for_training = np.array(embeds_for_training)
    faiss_index = faiss.index_factory(embeds_for_training.shape[1], index)
    faiss_index.train(embeds_for_training)
    faiss_index.add(embeds_for_training)

    return faiss_index


def index(args):
    chunk_files = []
    for file_type in ["*.pkl", "*.h5"]:
        chunk_files.extend(glob.glob(os.path.join(args.input_folder, file_type)))

    all_ids = []
    faiss_index = None
    embeds_for_training = []
    for i, chunk_file in enumerate(chunk_files):
        ids, embeddings = _read_file(chunk_file)
        all_ids.extend(ids)
        if args.n_chunks_for_training < 1 or i < args.n_chunks_for_training:
            embeds_for_training.extend(embeddings)
        else:
            if not faiss_index:
                # Create and train the index
                faiss_index = _create_index(embeds_for_training, args.index)
                embeds_for_training = None

            # Add the embeddings to the index
            faiss_index.add(embeddings)

    if not faiss_index:
        faiss_index = _create_index(embeds_for_training, args.index)

    # Save the index
    os.makedirs(args.output_folder, exist_ok=True)
    faiss.write_index(faiss_index, os.path.join(args.output_folder, f"{args.index_name}.index"))
    with open(os.path.join(args.output_folder, f"{args.index_name}.txt"), "w") as f:
        f.write("\n".join(map(str, all_ids)))


def register_command(subparsers):
    parser = subparsers.add_parser("index", help="Create a FAISS index for an embedded dataset.")
    parser.add_argument(
        "-i", "--input_folder", type=str, help="Input folder containing the embedded documents (.pkl/.h5 files)."
    )
    parser.add_argument("-o", "--output_folder", type=str, help="Output folder to store the index.")
    parser.add_argument("-n", "--index_name", type=str, help="Name of the index.")
    parser.add_argument(
        "--index",
        type=str,
        help="Definition of the FAISS index to be used. See https://github.com/facebookresearch/faiss/wiki/The-index-factory for the string format.",
    )
    parser.add_argument(
        "--n_chunks_for_training", type=int, default=-1, help="Number of chunks to use for training the index."
    )
    parser.set_defaults(func=index)
