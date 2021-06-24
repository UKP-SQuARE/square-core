## Framework

![SQuARE Datastore API](https://user-images.githubusercontent.com/71278644/123296137-ac33ba00-d516-11eb-9c87-de7203c1e459.png)

## Reference
- The demo system is mainly adapted from [vespa/semantic-qa-retrieval](https://github.com/vespa-engine/sample-apps/tree/master/semantic-qa-retrieval)
- Tutorial for supporting multiple-embedding system like [ColBERT](https://github.com/stanford-futuredata/ColBERT): [vespa/msmarco-ranking](https://github.com/vespa-engine/sample-apps/blob/master/msmarco-ranking/passage-ranking.md)
- [Official documentation](https://docs.vespa.ai/en/vespa-quick-start.html)

## Dependency
- Docker
- Jave 11: **The version number is very important!**
- Python 3 (transformers needed)
- Linux x86_64

## Usage
First pull the core docker container of Vespa:
```shell
$ docker pull vespaengine/vespa
```

Start the Vespa engine:
```shell
$ docker run --detach --name vespa --hostname vespa-container   --publish 8080:8080 --publish 19071:19071   vespaengine/vespa
```

Wait and check the status until one gets 200 OK:
```shell
$ curl -s --head http://localhost:19071/ApplicationStatus
```

Upload the application package to the Vespa engine:
```shell
$ (cd application && zip -r - .) | \
  curl --header Content-Type:application/zip --data-binary @- \
  localhost:19071/application/v2/tenant/default/prepareandactivate
```

Wait and check the status until one gets 200 OK:
```shell
$ curl -s --head http://localhost:8080/ApplicationStatus
```

Download the Vespa tool for uploading data:
```shell
$ curl -L -o vespa-http-client-jar-with-dependencies.jar \
  https://search.maven.org/classic/remotecontent?filepath=com/yahoo/vespa/vespa-http-client/7.391.28/vespa-http-client-7.391.28-jar-with-dependencies.jar
```

Download the sample data (extract from MS MARCO):
```
wget https://public.ukp.informatik.tu-darmstadt.de/kwang/tutorial/vespa/dense-retrieval/msmarco/sample-feed.jsonl
```

Upload the sample data as corups:
```python
$ java -jar vespa-http-client-jar-with-dependencies.jar \
  --file sample-feed.jsonl --endpoint http://localhost:8080
```

Run the API and input an query:
```
$ python query_api.py
what is the population of achill island?
```

Remove the container after usage:
```
docker rm -f vespa
```
