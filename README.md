# Local Deployment of Minimal SQuARE

This branch hosts a minimal version of SQuARE for the convenience of local deployment.

To get started, please run:
```
bash install-local.sh
```
to generate a `docker-compose.yaml` file.

And then:
```bash
docker-compose up -d
cd local_deploy
python deploy_ds.py  # Tested with Python 3.7.13 
```

This will start the minimal SQUARE service and run the example script `local_deploy/deploy_ds.py` to 
- Download example corpus scifact;
- Upload the corpus (to the ES in SQUARE);
- Do BM25 search;
- Embed and index the corpus with DPR;
- Start a Faiss container to load the built dense index;
- Do dense search.