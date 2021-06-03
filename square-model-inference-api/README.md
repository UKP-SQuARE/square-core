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
<!-- ```bash
pip install -r requirements
```  -->

```sh
python -m venv venv
source venv/bin/activate
make install
```

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


