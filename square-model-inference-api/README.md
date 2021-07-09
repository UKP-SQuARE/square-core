# SQuARE Model API
Inference API that supports SOTA (QA) models & adapters. 
Receives input and returns prediction and other artifacts (e.g. attention scores)

## Project structure

TODO
```
├───tests
│   ├───test_api
│   └───test_service
├───auth_server
│   └───auth_api
├───nginx
├───inference_server
│   ├───square_model_inference
│   │   ├───api                  - Model API
│   │   │   ├───routes
│   │   ├───core                 
│   │   ├───models               - Pydantic model definitions for in-/ output
│   │   ├───inference
```

## Requirements

Python 3.7+, Docker (optional), Make (optional)

## Installation
Install the required packages in your local environment (ideally virtualenv, conda, etc.).
```bash
pip install -r inference_server/requirements1.txt
pip uninstall -y -r inference_server/uninstall_requirements.txt
pip install -r inference_server/requirements2.txt
```
or
```sh
make install
```
**Why two requirement.txt and why the uninstall?**  
`sentence-transformers` depends on `transformers` and it will be installed along with it.
However, we use `adapter-transformers` (a fork of `transformers`) in this project.
Both `transformers` and `adapter-transformers` use the same namespace so they conflict.
Thus, we first install `sentence-transformers` along with `transformers`, 
uninstall `transformers`, and finally install `adapter-transformers`.

#### Running Localhost

```sh
make run
```

#### Running Via Docker

```sh
make deploy
```

#### Running Tests

```sh
make test
```

## Setup
TODO

## Run without `make` for development

1. Start your  app with: 
```bash
PYTHONPATH=./inference_server uvicorn main:app --reload
```

2. Go to [http://localhost:8000/docs](http://localhost:8000/docs) or  [http://localhost:8000/redoc](http://localhost:8000/redoc) for alternative swagger


## Run Tests with using `make`

Install testing libraries and run `tox`:
```bash
pip install tox pytest flake8 coverage bandit
tox
```
This runs tests and coverage for Python 3.8 and Flake8, Bandit.


