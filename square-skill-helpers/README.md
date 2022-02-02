# SQuARE Skill Helpers
This package facilitates the interaction with UKP-SQuARE APIs. Currently, interacting with thie Models and Datastores is supported. This helps when implementing Skills.

## Installation
To install the latest stable version:
```bash
pip install git+https://github.com/UKP-SQuARE/square-skill-helpers.git@v0.0.4
```
To install from the master branch:
```bash
pip install git+https://github.com/UKP-SQuARE/square-skill-helpers.git
```

## Usage
After installing, the and Datastore and Model API can be called easily. Before running the code, environment variables need to be set. The env file can be loaded via the `SquareSkillHelpersConfig` be providing the path, or the environment variables can be set before running the code.
```bash
SQUARE_API_URL=https://square.ukp-lab.de/api
DATA_API_KEY=<DATA_API_KEY_GOES_HERE>
```

```python3
from square_skill_helpers.config import SquareSkillHelpersConfig
from square_skill_helpers.square_api import DataAPI, ModelAPI

if __name__ == "__main__":
    # 1. setup DataAPI and ModelAPI instances
    # set `SQUARE_API_URL` and `DATA_API_KEY` variables in your environment 
    # or provide a `.env` file to load from
    config = SquareSkillHelpersConfig.from_dotenv(".env.example")
    data_api = DataAPI(config)
    model_api = ModelAPI(config)

    query = "When was TU Darmstadt established?"
    # 2. Call DataAPI
    data = await data_api(datastore_name="nq", index_name="dpr", query=query)
    context = [d["document"]["text"] for d in data]
    context_score = [d["score"] for d in data]
    for i, (c, s) in enumerate(zip(context, context_score)):
        print(f"#{i} (score={s}) {c[:50] + '...'}")
    # #1 (score=70.325) "Technische Universität Darmstadt The Technische U...
    # #2 (score=69.928) "TU9, a network of the most notable German ""Techn...
    # #3 (score=69.208) "Texas Lutheran University Texas Lutheran Universi...
    # ...

    # 3. Call ModelAPI
    model_request = {
        "input": [[query, c] for c in context],
        "task_kwargs": {"topk": 1},
        "adapter_name": "qa/squad2@ukp"
    }

    model_api_output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="question-answering", 
        model_request=model_request
    )
    print(model_api_output['answers'][0])
    # [{'score': 0.9184646010398865, 'start': 275, 'end': 279, 'answer': '1877'}]
```
