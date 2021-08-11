## Framework

![SQuARE Datastore API](https://user-images.githubusercontent.com/71278644/123296137-ac33ba00-d516-11eb-9c87-de7203c1e459.png)

## Reference
- The demo system is mainly adapted from [vespa/semantic-qa-retrieval](https://github.com/vespa-engine/sample-apps/tree/master/semantic-qa-retrieval)
- Tutorial for supporting multiple-embedding system like [ColBERT](https://github.com/stanford-futuredata/ColBERT): [vespa/msmarco-ranking](https://github.com/vespa-engine/sample-apps/blob/master/msmarco-ranking/passage-ranking.md)
- [Official documentation](https://docs.vespa.ai/en/vespa-quick-start.html)

## Requirements

- Docker
- Java 11: **The version number is very important!**
- Python 3.8+

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

You can download some example documents here:
https://public.ukp.informatik.tu-darmstadt.de/kwang/tutorial/vespa/dense-retrieval/msmarco/0.jsonl

... and their corresponding embeddings here:
https://public.ukp.informatik.tu-darmstadt.de/kwang/tutorial/vespa/dense-retrieval/msmarco/0.hdf5

In case documents or embeddings should be provided from a local folder, a development file server can be started:
```
cd /path/to/folder/with/documents
python -m http.server 3000
```
