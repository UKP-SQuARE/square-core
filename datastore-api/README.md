# SQuARE Datastore API

API for storing, indexing and retrieving document corpora, powered by [Elasticsearch](https://www.elastic.co/elasticsearch/) and [FAISS](https://github.com/facebookresearch/faiss).

## Overview

![SQuARE Datastore API](images/overview.png)

The Datastore API is dependent upon the following services:

- Required (automatically via Docker):
  - **Elasticsearch** (for storing documents and sparse retrieval)
  - **Traefik** (for routing search requests)
- Optional (manual setup required):
  - **FAISS** web service containers (for storing dense document embeddings): see [the section on dense retrieval](#configure-dense-retrieval-with-faiss) on how to setup.
  - **SQuARE Model API** (for dense document retrieval)

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

Start the server:
```
make run
```

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

## Upload documents

In general, there are two ways to upload documents to the server: via the REST interface of the Datastore API or via the `upload.py` script.

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

### Uploading via `upload.py`

As an example, we upload the Wikipedia split used by DPR (containing 21M passages) into a datastore named "wiki".

1. First, we download and unzip the documents:
    ```
    curl https://dl.fbaipublicfiles.com/dpr/wikipedia_split/psgs_w100.tsv.gz -o psgs_w100.tsv.gz
    gunzip psgs_w100.tsv.gz
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
    python upload.py\
      -s wiki \
      -t <access_token> \
      psgs_w100.tsv
    ```

## Configure dense retrieval with FAISS

To enable dense document retrieval with FAISS, the Datastore API relies on [FAISS web service containers](https://github.com/kwang2049/faiss-instant) that provide FAISS indices for the documents in a datastore.
Each index in each datastore is corresponds to one FAISS web service container.
The document embedding computation and FAISS index creation are performed offline, i.e. not via the Datastore API itself.

Let's see how to add a dense retrieval index to an existing datastore (`"wiki"`).
The new index should use Facebook's DPR model and should be called `"dpr"`.

1. Embed the document corpus using the document encoder model & create a FAISS index in the correct format. Refer to https://github.com/kwang2049/faiss-instant for more on this.

2. Register the new index with its name via the Datastore API:
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

3. Specify the FAISS web service container for the new index: Open the [docker-compose.yml](docker-compose.yml) and in the section for FAISS service containers, add the following:
    ```
    faiss-wiki-dpr:
      image: kwang2049/faiss-instant:latest
      volumes:
        - /local/path/to/index:/opt/faiss-instant/resources
      labels:
        - "traefik.enable=true"
        - "square.datastore=/wiki/dpr"
    ```

4. Restart the Docker Compose setup:
    ```
    docker compose up -d
    ```
