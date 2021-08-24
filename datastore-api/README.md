# SQuARE Datastore API

API for storing, indexing and retrieving document corpora, powered by [Vespa](https://vespa.ai).

## Overview

![SQuARE Datastore API](https://user-images.githubusercontent.com/71278644/123296137-ac33ba00-d516-11eb-9c87-de7203c1e459.png)

## Requirements

- Python 3.8+
- Docker
- Java 11
- Make (optional)

Python requirements via pip (ideally with virtualenv):
```
pip install -r requirements.txt
```
... or via conda:
```
conda env create -f environment.yml
```

## Setup

### Docker containers

We use Docker containers for:
- MongoDB
- Vespa

Everything can be started via Docker Compose:
```
docker compose up --detach
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

Got to **http://localhost:8000/docs** for interactive documentation.

### Tests

Run API tests (requires Vespa to be running):
```
make test
```

## Demo configuration & data

To showcase the API methods, we configure a demo datastore and fill it with some data.
The demo has a datastore `wiki` with two indices `bm25` and `dpr`.

Initialize the app and the demo datastore:
```
make demo-init
```

Start the server as usual:
```shell
make run
```

## Upload data

In general, there are two ways to upload documents and embeddings to the server: via the REST interface of the Datastore API or directly via the Vespa API.
**When uploading larger amounts of data, it is highly recommended to upload directly via Vespa.**

### Uploading via the REST API

The Datastore API provides different methods for uploading documents and embeddings.
Documents are expected to be uploaded as .jsonl files, embeddings as .hdf5 files.

You can download some example documents [here](https://public.ukp.informatik.tu-darmstadt.de/kwang/tutorial/vespa/dense-retrieval/msmarco/0.jsonl) and their corresponding embeddings [here](https://public.ukp.informatik.tu-darmstadt.de/kwang/tutorial/vespa/dense-retrieval/msmarco/0.hdf5).

Now, the documents file can be uploaded to the Datastore API as follows (uploading embeddings is similar):
```
curl -X 'POST' \
  'http://localhost:8002/datastores/wiki/documents/upload' \
  -H 'Authorization: abcdefg' \
  -F 'file=@0.jsonl'
```

### Uploading via Vespa

Uploading to Vespa can be done using the [Vespa HTTP Client](https://docs.vespa.ai/en/vespa-http-client.html).

1. Download the Vespa HTTP Client:
    ```
    curl -L -o vespa-http-client-jar-with-dependencies.jar \
      https://search.maven.org/classic/remotecontent?filepath=com/yahoo/vespa/vespa-http-client/7.391.28/vespa-http-client-7.391.28-jar-with-dependencies.jar
    ```

3. Prepare data in .jsonl format: Uploaded files should match [Vespa's JSON format](https://docs.vespa.ai/en/reference/document-json-format.html). An example feed can be found [here](https://raw.githubusercontent.com/vespa-engine/sample-apps/master/dense-passage-retrieval-with-ann/sample-feed.jsonl).

2. Upload .jsonl file to Vespa:
    ```
    java -jar vespa-http-client-jar-with-dependencies.jar --file sample-feed.jsonl --endpoint http://localhost:8082
    ```

## References
- The demo system is mainly adapted from [vespa/semantic-qa-retrieval](https://github.com/vespa-engine/sample-apps/tree/master/semantic-qa-retrieval)
- Tutorial for supporting multiple-embedding system like [ColBERT](https://github.com/stanford-futuredata/ColBERT): [vespa/msmarco-ranking](https://github.com/vespa-engine/sample-apps/blob/master/msmarco-ranking/passage-ranking.md)
- [Official documentation](https://docs.vespa.ai/en/vespa-quick-start.html)
