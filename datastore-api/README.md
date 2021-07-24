## Framework

![SQuARE Datastore API](https://user-images.githubusercontent.com/71278644/123296137-ac33ba00-d516-11eb-9c87-de7203c1e459.png)

## Reference
- The demo system is mainly adapted from [vespa/semantic-qa-retrieval](https://github.com/vespa-engine/sample-apps/tree/master/semantic-qa-retrieval)
- Tutorial for supporting multiple-embedding system like [ColBERT](https://github.com/stanford-futuredata/ColBERT): [vespa/msmarco-ranking](https://github.com/vespa-engine/sample-apps/blob/master/msmarco-ranking/passage-ranking.md)
- [Official documentation](https://docs.vespa.ai/en/vespa-quick-start.html)

## Requirements
- Docker
- Java 11: **The version number is very important!**
- Python 3 (transformers needed)

Python requirements:
```
pip install -r requirements.txt
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

### Demo configuration & data

To showcase the API methods, we configure a demo datastore and fill it with some data.
The demo has a datastore `wiki` with two indices `bm25` and `dpr`.

After starting Docker, first check the Vespa status until it returns HTTP 200:
```shell
curl -s --head http://localhost:19071/ApplicationStatus
```

Initialize the app and the demo datastore:
```
python init_app.py
```

Wait and check the Vespa app status until you get HTTP 200:
```shell
curl -s --head http://localhost:8080/ApplicationStatus
```

Download the Vespa tool for uploading data:
```shell
curl -L -o vespa-http-client-jar-with-dependencies.jar \
  https://search.maven.org/classic/remotecontent?filepath=com/yahoo/vespa/vespa-http-client/7.391.28/vespa-http-client-7.391.28-jar-with-dependencies.jar
```

Download the sample data (extract from MS MARCO):
```
wget https://public.ukp.informatik.tu-darmstadt.de/kwang/tutorial/vespa/dense-retrieval/msmarco/sample-feed.jsonl
```
Modify the data for our app:
```
sed -i 's/text_embedding/dpr_embedding/g' sample-feed.jsonl
```

Upload the sample data to the datastore:
```
java -jar vespa-http-client-jar-with-dependencies.jar --file sample-feed.jsonl --endpoint http://localhost:8080
```

### API server

Make sure the Vespa app server is running (see above):
```shell
curl -s --head http://localhost:8080/ApplicationStatus
```

Start the FastAPI server:
```
uvicorn app.main:app --reload --reload-dir app
```

Got to **http://localhost:8000/docs** for interactive documentation.
