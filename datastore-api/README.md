# SQuARE Datastore API

API for storing, indexing and retrieving document corpora, powered by [Elasticsearch](https://www.elastic.co/elasticsearch/) and [FAISS](https://github.com/facebookresearch/faiss).

## Overview

The Datastore API consists of or is dependent upon the following components and services:

- Required (automatically via Docker):
  - REST API frontend using **FastAPI** (the unified interface to access the API services)
  - **Elasticsearch** (for storing documents and sparse retrieval)
  - **Traefik** (for routing search requests)
- Optional (manual setup required):
  - **FAISS** web service containers (for storing dense document embeddings): see [the section on dense retrieval](#configure-dense-retrieval-with-faiss) on how to setup.
  - **SQuARE Model API** (for dense document retrieval)
  - [`square-data-cli`](#square-data-cli) (provides client-side tools for working with the API)

## Quick (production) setup

1. Open the [docker-compose.yml](docker-compose.yml). Find the service declaration for `datastore_api` and uncomment it. In the `environment` section, optionally set an API key and the connection to the Model API.

2. Run the Docker setup:
   ```
   docker compose up -d
   ```
   Check **http://localhost:7000/docs** for interactive documentation.

3. [Upload documents](#upload-documents).

4. For dense retrieval, [configure a FAISS container](#configure-dense-retrieval-with-faiss) per datastore index.

## Development setup

### Requirements

- Python 3.7+
- Docker
- Make (optional)

Python requirements via pip (ideally with virtualenv):
```
pip install -r requirements.txt
```
... or via conda:
```
conda env create -f environment.yml
```

### Docker containers

We use Docker containers for:
- Elasticsearch
- Traefik

Additionally, the FAISS storage for each datastore index requires its own container.
Check the [FAISS configuration](#configure-dense-retrieval-with-faiss) section for more.

Everything can be started via Docker Compose:
```
docker compose up -d
```

And teared down again after usage:
```
docker compose down
```

### API server

**Configuration:** Before starting the server, a few configuration options can be set via environment variables or a `.env` file. See [here](.env) for an example configuration and [here](app/core/config.py) for all available options.

**Running:**
```
make run
```
By default, the server will run at port 7000.

Check **http://localhost:7000/docs** for interactive documentation.
See below for uploading documents and embeddings.

### Tests

Run integration tests:
```
make test
```
Run API tests (does not require dependency services):
```
make test-api
```

## `square-data-cli`

To simplify some common workflows, the Datastore API comes with a simple CLI.
It allows embedding documents, creating FAISS indices for dense retrieval and uploading documents to the server.
The CLI can be found in the `scripts` folder and can be installed from the cloned repository with:

```
pip install -U ./scripts/.
```

or from remote with:

```
pip install -U git+https://github.com/UKP-SQuARE/square-core.git#subdirectory=datastore-api/scripts
```

If installation was successful, type `square-data-cli --help` to view the available commands.

## Upload documents

In general, there are two ways to upload documents to the server: via the REST interface of the Datastore API or via the `square-data-cli` CLI.

### Uploading via the REST API

The Datastore API provides different methods for uploading documents.
Documents are expected to be uploaded as `.jsonl` files.

We first create a demo datastore to upload some documents to:
```
curl -X 'PUT' \
  'http://localhost:7000/datastores/demo' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "name": "id",
    "type": "long"
  },
  {
    "name": "title",
    "type": "text"
  },
  {
    "name": "text",
    "type": "text"
  }
]'
```

Some example documents adhering to the required format can be found at `tests/fixtures/0.jsonl`.
We can upload these documents to the Datastore API as follows:
```
curl -X 'POST' \
  'http://localhost:7000/datastores/wiki/demo/upload' \
  -H 'Authorization: abcdefg' \
  -F 'file=@tests/fixtures/0.jsonl'
```

### Uploading via CLI

As an example, we upload a portion of the Wikipedia split used by DPR (containing 21M passages in total) into a datastore named "wiki".
Make sure to [have the CLI set up](#square-data-cli).

1. First, we download and unzip the documents:
    ```
    curl https://dl.fbaipublicfiles.com/dpr/wikipedia_split/psgs_w100.tsv.gz -o psgs_w100.tsv.gz
    gunzip psgs_w100.tsv.gz
    ```
    For testing purposes, we only upload the first 10,000 documents of the corpus:
    ```
    head -n 10001 psgs_w100.tsv > psgs_w100_10k.tsv
    ```

2. Create the datastore:
    ```
    curl -X 'PUT' \
      'http://localhost:7000/datastores/wiki' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '[
      {
        "name": "id",
        "type": "long"
      },
      {
        "name": "title",
        "type": "text"
      },
      {
        "name": "text",
        "type": "text"
      }
    ]'
    ```

3. Upload documents:
    ```
    square-data-cli upload -s wiki -t <access_token> psgs_w100_10k.tsv
    ```

## Configure dense retrieval with FAISS

To enable dense document retrieval with FAISS, the Datastore API relies on [FAISS web service containers](https://github.com/kwang2049/faiss-instant) that provide FAISS indices for the documents in a datastore.
Each index in each datastore is corresponds to one FAISS web service container.
The document embedding computation and FAISS index creation are performed offline, i.e. not via the Datastore API itself.

Let's see how to add a dense retrieval index to an existing datastore (`"wiki"`).
We will re-use the portion of the Wikipedia corpus (`psgs_w100_10k.tsv`) [downloaded earlier](uploading-via-cli).
The new index should use Facebook's DPR model and should be called `"dpr"`.

1. Embed the document corpus using the document encoder model.
Make sure to [have the CLI set up](#square-data-cli):
    ```
    square-data-cli embed \
      --model_name facebook/dpr-ctx_encoder-single-nq-base \
      --model_type transformer \
      --batch_size 128 \
      --chunk_size 5000 \
      -i psgs_w100_10k.tsv \
      -o output/embeddings/documents.pkl
    ```

2. Create a FAISS index from the embedded corpus:
    ```
    square-data-cli index \
      --name dpr \
      --index "IVF8,Flat" \
      --n_chunks_for_training 2 \
      -i output/embeddings \
      -o output/indices
    ```
    Please refer to [the FAISS wiki](https://github.com/facebookresearch/faiss/wiki/The-index-factory) for the syntax of the index string argument.

3. Register the new index with its name via the Datastore API:
    ```
    curl -X 'PUT' \
    'http://localhost:7000/datastores/wiki/indices/dpr' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "doc_encoder_model": "facebook/dpr-ctx_encoder-single-nq-base",
      "query_encoder_model": "facebook/dpr-question_encoder-single-nq-base",
      "embedding_size": 768
    }'
    ```

4. On the server side, specify the FAISS web service container for the new index: Open the [docker-compose.yml](docker-compose.yml) and in the section for FAISS service containers, add the following:
    ```
    faiss-wiki-dpr:
      image: kwang2049/faiss-instant:latest
      volumes:
        - /local/path/to/index:/opt/faiss-instant/resources
      labels:
        - "traefik.enable=true"
        - "traefik.http.services.faiss-wiki-dpr.loadbalancer.server.port=5000"
        - "square.datastore=/wiki/dpr"
    ```

5. Now, upload the FAISS index files created in step 2 to the server. Make sure to place both generated files in the folder specified in the Docker Compose setup in step 4 (`/local/path/to/index`).

6. Finally, restart the Docker Compose setup:
    ```
    docker compose up -d
    ```
