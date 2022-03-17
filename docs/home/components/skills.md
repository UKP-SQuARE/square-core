---
sidebar_position: 3
---

# Skills
Skills define how the user query should be processed by the Datastores and Models services and how the answers are obtained. For question answering, this might involve retrieving background knowledge from the Datastores and/or extracting spans from context using a particular Model and Adapter.

Skills can be added dynamically to UKP-SQuARE. Check out the 👉 [Add New Skills](#Add-New-Skills) for details.

For a list of available skills, see 👉 [Publicly Available Skills](#publicly-available-skills).

## Add New Skills
### The Predict Function
To create a new skill, simply the predict function needs to be implemented. For facilitating this, we provide two packages: [SQuARE-skill-helpers*](https://github.com/UKP-SQuARE/square-skill-helpers) and [SQuARE-skill-api](https://github.com/UKP-SQuARE/square-skill-api). The skill-helpers package facilitates the interaction with other SQuARE services, such as Datastores and Models. The skill-api package wraps the final predict function creating an API that can be accessed by SQuARE. Further, it provides dataclasses (pydantic) for input and output of the predict function.

As mentioned above mainly a predict function, defining the pipeline needs to be implemented. 
First, install the required packages:
```bash
pip install git+https://github.com/UKP-SQuARE/square-skill-helpers.git@v0.0.4
pip install git+https://github.com/UKP-SQuARE/square-skill-api.git@v0.0.11 
```
Next, we can implement the `predict` function:
```python3

# import utility classes from `square_skill_api` and `square_skill_helpers`
from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest
from square_skill_helpers.config import SquareSkillHelpersConfig
from square_skill_helpers.square_api import ModelAPI, DataAPI

# create a config instance. This loads environment variables required for connecting to SQuARE services. Create an `.env` file when hosting yourself or on the cloud.
config = SquareSkillHelpersConfig.from_dotenv()
# create instances of the DataAPI and ModelAPI for interacting with SQuAREs Datastores and Models
data_api = DataAPI(config)
model_api = ModelAPI(config)

# this is the standard input that will be given to every predict function. See the details in the `square_skill_api` package for all available inputs.
async def predict(request: QueryRequest) -> QueryOutput:

    # Call the Datastores using the `data_api` object
    data = await data_api(datastore_name="nq", index_name="dpr", query=request.query)
    context = [d["document"]["text"] for d in data]
    context_score = [d["score"] for d in data]

    # prepare the request to the Model API. For details, see Model API docs 
    model_request = {
        "input": [[request.query, c] for c in context],
        "task_kwargs": {"topk": 1},
        "adapter_name": "qa/squad2@ukp"
    }

    # Call Model using the `model_api` object
    model_api_output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="question-answering", 
        model_request=model_request
    )

    # return an QueryOutput object created using the question-answering constructor
    return QueryOutput.from_question_answering(
        model_api_output=model_api_output,
        context=context,
        context_score=context_score
    )

```
### Adding Via Pull Request
If you want to run your Skill directly on SQuARE hardware, you can submit a [pull request](https://github.com/UKP-SQuARE/square-core/pulls) with the following changes:
1. Put your skill function in a file under: `./skills/<skill-name>/skill.py`
2. Add you skill in the [config.yaml](https://github.com/UKP-SQuARE/square-core/blob/master/config.yaml). Give the skill the same name as the folder under skills.
3. Once you pull request is approved, your skill url will be `http://<skill-name>:<port>`

### Adding Self-Hosted or Cloud Skills
#### Azure Functions
1. Login to [Azure](https://portal.azure.com/)
2. Create a new function app
    - Select to publish _Code_
    - Select _Python_ as runtime stack.
3. Once the deployment is complete, under Next Steps, click _create function_ and follow the setup instructions according to your development environment.
4. During the setup:
    - Use the _HTTP Trigger_ template
    - Name the function _query_ (*This is very important, since this will determine the url under which your function will be available.*)
    - Select _anonymous_ as authorization level.
5. Develop your skill in the __init__.py
6. Add environment variables to the `local.settings.json` file under `Values`.
6. Deploy your skill according to the instructions
7. Copy the URL of your deployment and use it when creating a skill in SQuARE without the trailing `/query` (e.g. https://myskill.azurewebsites.net/api). 
An example repository can also be found at [UKP-SQuARE/cloud-example-azure](https://github.com/UKP-SQuARE/cloud-example-azure)
## Publicly Available Skills
| Name | Retrieval Model | Datastore | Reader Model | Reader Adapter | Type | Code |
|---|---|---|---|---|---|---|
| BoolQ BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [boolq](https://huggingface.co/AdapterHub/bert-base-uncased-pf-boolq) | categorical | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| BoolQ RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [boolq](https://huggingface.co/AdapterHub/roberta-base-pf-boolq) | categorical | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| CommonsenseQA BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [commonsense_qa](https://huggingface.co/AdapterHub/bert-base-uncased-pf-commonsense_qa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| CommonsenseQA RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [commonsense_qa](https://huggingface.co/AdapterHub/roberta-base-pf-commonsense_qa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| CosmosQA BERT |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [cosmos_qa](https://huggingface.co/AdapterHub/bert-base-uncased-pf-cosmos_qa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| CosmosQA RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [cosmos_qa](https://huggingface.co/AdapterHub/roberta-base-pf-cosmos_qa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| DROP BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [drop](https://huggingface.co/AdapterHub/bert-base-uncased-pf-drop) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| DROP RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [drop](https://huggingface.co/AdapterHub/roberta-base-pf-drop) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| HotpotQA BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [hotpotqa](https://huggingface.co/AdapterHub/bert-base-uncased-pf-hotpotqa) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| HotpotQA RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [hotpotqa](https://huggingface.co/AdapterHub/roberta-base-pf-hotpotqa) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| MultiRC BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [multirc](https://huggingface.co/AdapterHub/bert-base-uncased-pf-multirc) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| MultiRC RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [multirc](https://huggingface.co/AdapterHub/roberta-base-pf-multirc) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| NarrativeQA BART Adapter |  |  | [bart-base](https://huggingface.co/facebook/bart-base) | [narrativeqa](https://huggingface.co/AdapterHub/narrativeqa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/generative-qa/skill.py) |
| NewsQA BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [newsqa](https://huggingface.co/AdapterHub/bert-base-uncased-pf-newsqa) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| NewsQA RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [newsqa](https://huggingface.co/AdapterHub/roberta-base-pf-newsqa) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| OpenBioASQ | [BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables) | Pubmed | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [squad_v2](https://huggingface.co/https://huggingface.co/AdapterHub/bert-base-uncased-pf-squad_v2) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/open-bioasq/skill.py) |
| OpenSQuAD | [dpr](https://huggingface.co/facebook/dpr-ctx_encoder-single-nq-base) | Wikipedia | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [squad_v2](https://huggingface.co/https://huggingface.co/AdapterHub/bert-base-uncased-pf-squad_v2) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/open-squad/skill.py) |
| OpenSQuAD | [distilbert](https://huggingface.co/sentence-transformers/msmarco-distilbert-base-tas-b) | msmarco | [roberta-base](https://huggingface.co/roberta-base) | [multirc](https://huggingface.co/AdapterHub/roberta-base-pf-multirc) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/open-extractive-qa/skill.py) |
| QuAIL BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [quail](https://huggingface.co/AdapterHub/bert-base-uncased-pf-quail) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| QuAIL RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [quail](https://huggingface.co/AdapterHub/roberta-base-pf-quail) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| QuaRTz RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [quartz](https://huggingface.co/AdapterHub/roberta-base-pf-quartz) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| Quoref BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [quoref](https://huggingface.co/AdapterHub/bert-base-uncased-pf-quoref) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| Quoref RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [quoref](https://huggingface.co/AdapterHub/roberta-base-pf-quoref) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| RACE BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [race](https://huggingface.co/AdapterHub/bert-base-uncased-pf-race) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| RACE RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [race](https://huggingface.co/AdapterHub/roberta-base-pf-race) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| SQuAD 1.1 BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [squad](https://huggingface.co/AdapterHub/bert-base-uncased-pf-squad) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| SQuAD 1.1 RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [squad](https://huggingface.co/AdapterHub/roberta-base-pf-squad) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| SQuAD 2.0 BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [squad_v2](https://huggingface.co/AdapterHub/bert-base-uncased-pf-squad_v2) | span-extraction | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/extractive-qa/skill.py) |
| Social-IQA BERT Adapter |  |  | [bert-base-uncased](https://huggingface.co/bert-base-uncased) | [social_i_qa](https://huggingface.co/AdapterHub/bert-base-uncased-pf-social_i_qa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |
| Social-IQA RoBERTa Adapter |  |  | [roberta-base](https://huggingface.co/roberta-base) | [social_i_qa](https://huggingface.co/AdapterHub/roberta-base-pf-social_i_qa) | multiple-choice | [code](https://github.com/UKP-SQuARE/square-core/blob/master/skills/multiple-choice-qa/skill.py) |

