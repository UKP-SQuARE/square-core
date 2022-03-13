---
sidebar_position: 4
---

# Tutorials
# Skill Development Tutorial

## Introduction

In this tutorial we implement a Skill for [UKP-SQuARE](https://square.ukp-lab.de). Generally, a Skill defines a pipeline through which a question is processed to eventually obtain an answer. SQuARE provides different ways of adding Skills to the platform, here we will focus on integrating the Skill directly in SQuARE. 

## Setup

### square-core

In order to host your Skill directly in SQuARE, you will eventually need to create a pull request in the github repository. Therefore, you should first create a fork of  [square-core](https://github.com/UKP-SQuARE/square-core) and clone the new repository to your local machine.

```bash
git clone https://github.com/<github-username>/square-core.git
```

### Virtual Environment Setup

To develop a Skill you will be mostly concerned with the contents of the `skill` directory. In this directory, we create a virtual python environment to install the required dependencies. Depending on your preferences there are different options for this. Here we will use the built-in python way:

```bash
cd skills
python -m venv .venv
source .venv/bin/activate
```

**Note**: We tested SQuARE mostly with python 3.7. But also succeeding versions should work.

Finally, we can install the dependencies required for Skill development by running:

```bash
pip install -r requirements.txt
```

### SQuARE Integration

In order for our skill to be created and deployed, we need to add it to the `config.yaml` file in the root folder. This is required as input to the automatic creation of skill services. You need to add a name and an author which needs to be your SQuARE username.

```yaml
skills:
  - name: boolq
	author: ukp
  # ...
  - name: open_domain_extractive_qa_tut
    author: your-square-username
```

## Skill Development

In this tutorial, we will implement an open-domain, extractive question answering skill. This Skill takes a question as input and automatically retrieves relevant information and finally extracts answers from those information.

First, we create a new folder in the skills directory with the same name as in the config.yaml (we call it `open_domain_extractive_qa_tut` in this tutorial) and create file called `skill.py`

```bash
mkdir -p open_domain_extractive_qa_tut && touch open_domain_extractive_qa_tut/skill.py
```

### Imports

Now we can start implementing the Skill, in the newly created `skill.py` file. We fist need to import some classes.

- `QueryRequest`: Class holding the input to the Skill from the UI.
- `QueryOutput`: Class for holding the output of the Skill to the UI.
- `DataAPI` & `ModelAPI`: Utility classes that facilitate the interaction with SQuARE's Datastores and Models

```python
import logging

from square_skill_api.models.request import QueryRequest
from square_skill_api.models.prediction import QueryOutput

from square_skill_helpers import DataAPI, ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()
data_api = DataAPI()
```

### Predict Function

Next, we develop the heart of the Skill: the prediction function. This function is executed, whenever our Skill is called from the UI to answer a query. 

Details of what input the Skill receives can be obtained by inspecting the QueryRequest class:

```python
class QueryRequest(BaseModel):

    query: str = Field(
        ..., description="The input to the model that is entered by the user"
    )
    skill_args: Dict[str, Any] = Field(
        {}, description="Optional values for specific parameters of the skill"
    )
    # ...
```

The `query` field holds the question the user has given as input to your skill.

The `skill_args` field is very powerful. Most importantly, if your skill requires context to answer a question, there will be a `context` field holding that text. Similarly, if your implement a multiple-choice skill, that selects a single answer from a set of given answer choices, there will be a `choices` field that is a list of strings. The `skill_args` can also be used to make your Skill configurable. For our skill, we do not need to make use of the `skill_args` since we only require the query.

#### Background Knowledge Retrieval

Now that we understand the input to the Skill, we will implement the background information retrieval using the DataAPI.

The `data_api` requires at least three parameters to obtain relevant documents:

1. `query`: The input query that is used to obtain background information.
2. `datastore_name`: This is the name of the dataset that originally provided the data. In this tutorial, we will use `nq` which stands for [Natural Questions](https://aclanthology.org/Q19-1026/) and is a snapshot from the English Wikipedia from December 20th, 2018.
3. `index_name`: This specifies the model that is used for creating the index. Generally, every datastore supports lexical retrieval using BM25. To use BM25, we could provide an empty string. For most other datastores, SQuARE also provide a suitable dense retrieval method. In case of Natural Questions, we can use the [Dense Passage Retrieval](https://aclanthology.org/2020.emnlp-main.550/) model, or shorthand `dpr`.

```python
async def predict(request: QueryRequest) -> QueryOutput:

	data_api_output = await data_api(
		query=request.query,
        datastore_name="nq",
        index_name="dpr",
	)
	context = [d["document"]["text"] for d in data_api_output]
	context_score = [d["score"] for d in data_api_output]

	# ...
```

From the response, we extract the texts of the retrieved documents and store it in a `context` variable for later use, as well as the associated scores of the documents (i.e. how relevant they are) to return this information later to the user.

#### Answer Extraction

Now that we have some context to answer the users query, we need to find the exact piece of text in the context that answers the questions. For this we will use SQuAREs Models.

The `model_api` requires at least three parameters to extract answers:

1. `model_request`: A dictionary holding the input to the model and additional, optional parameters like an Adapter that should be used (more details about adapters later).
2. `model_name`: The name of the model in SQuARE that shall be used to process the input.
3. `pipeline`: Specifies how the input should be processed. Currently, we support (`embedding`, `generation`, `sequence-classification`, `token-classification`, and `question-answering`).

```python
async def predict(request: QueryRequest) -> QueryOutput:

    # ...

    model_request = {
        "input": [[request.query, c] for c in context],
        "adapter_name": "AdapterHub/roberta-base-pf-squad_v2",
    }
    model_api_output = await model_api(
    model_request=model_request,
        model_name="roberta-base",
    pipeline="question-answering",  
    )
```

#### Response

Since the Skill will be part of an API, we need to exactly stick to the output schema. For this we have prepared the `QueryOutput` class that comes with constructors for each pipeline. Therefore, we will use the `QueryOutput.from_question_answering` constructor. It will take care of bringing together the `context`, `context_score` and `model_api_output` for displaying everything nicely in the UI to the user.

```python
async def predict(request: QueryRequest) -> QueryOutput:

	# ...

	return QueryOutput.from_question_answering(
        model_api_output=model_api_output, 
        context=context, 
        context_score=context_score
    )
```

### Local Testing

In order to test the skill locally with the datastores and models in SQuARE, we first need to register the skill in SQuARE to obtain some credentials. For this, we go to [square.ukp-lab.de](https://square.ukp-lab.de), sign in and go to My Skills. We create a new Skill by entering a name, selecting a Skill Type (for this tutorial it would be `span-extraction`) and provide an URL. Right now, we do not have a working URL yet, however, eventually the skill will be running under the skill name. So we can already put it `http://open_domain_extractive_qa_tut`. Once you save the Skill, you will see a `Client ID` and `Client Secret`.  These are the credentials for the Skill to access SQuARE Datastores and Models. We will provide them later as environment variables when we start the API.

To run the entire API locally, we need to change the `main.py` file, to import the predict function from the correct file. See the example below. 

```python
# skills/main.py

# from skill import predict
from open_domain_extractive_qa_tut.skill import predict

# ...
```

Now we can run the Skill locally with the command below. This will start a uvicorn server, running an API to the predict function.

```bash
SQUARE_API_URL=https://square.ukp-lab.de/api KEYCLOAK_BASE_URL=https://square.ukp-lab.de REALM=square CLIENT_ID=<your-client-id> CLIENT_SECRET=<your-client-secret> uvicorn main:app --reload
```

The best way to test the Skill is to go to [localhost:8000/docs](http://127.0.0.1:8000/docs).

Finally, we can go to the [/query](http://localhost:8000/docs#/query/Skill_Query_query_post) endpoint and enter a query. For example:

```json
{
  "query": "When did Germany become reunified?"
}
```

This should return predictions like this:

```json
{
  "predictions": [
    {
      "prediction_score": 0.9750158786773682,
      "prediction_output": {
        "output": "1990,",
        "output_score": 0.9750158786773682
      },
      "prediction_documents": [
        {
          "index": "",
          "document_id": "",
          "document": "\"... Germany was reunited in 1990, following the decline and fall of the SED as the ruling party of the GDR. At\"",
          "span": [
            541,
            546
          ],
          "url": "",
          "source": "",
          "document_score": 80.47113037109375
        }
      ]
    },
```

## Submitting to SQuARE

Now that we have developed the Skill, we can submit it to SQuARE by creating a [pull request](https://github.com/UKP-SQuARE/square-core/pulls) from our fork. (Note: Don’t forget to undo the changes in `skills/main.py`).

Once the changes are approved and deployed, we can use our Skill on SQuARE, make it public to be used by others and compare its performance to other Skills!
