# Local Deployment of Minimal SQuARE

This branch hosts a minimal version of SQuARE for the convenience of local deployment.

To get started, please run:
```
pip install -r local_deploy/requirements.txt
bash install-local.sh
```
to generate a `docker-compose.yaml` file (and a authentication token for local deployment in `./local_deploy`)

And then:
```bash
docker-compose up -d
python local_deploy/embed_query.py  # An example of calling model API to embed a query
python local_deploy/deploy_ds.py  # An example of deploying a new datastore
```

> This will start the minimal SQUARE service and run the example script `local_deploy/deploy_ds.py` to 
> - Download example corpus scifact;
> - Upload the corpus (to the ES in SQUARE);
> - Do BM25 search;
> - Embed and index the corpus with DPR (GPU 1min, CPU 30min);
> - Start a Faiss container to load the built dense index;
> - Do dense search.

One can also get access to the [SWAGGER UI](https://swagger.io/tools/swagger-ui/) page for the interactive API of Datastores. To do so, one can do 
```bash
export SQUARE_PRIVATE_KEY_FILE="local_deploy/private_key.pem"
square_token  # A Python entry point from `square_auth`
```
to get the token for authorization. Thereafter, just open http://localhost:7000/docs# and type in the token by clicking on "Authorize". Then you are ready to go.
