# Skills
Skills define how the user query should be processed by the Datastores and Models services and how the answers are obtained. For question answering, this might involve retrieving background knowledge from the Datastores and/or extracting spans from context using a particular Model and Adapter.

Skills can be added dynamically to UKP-SQuARE. Check out the 👉 [Add New Skills](#Add-New-Skills) for details.

For a list of available skills, see 👉 [Publicly Available Skills](Publicly-Available-Skills).

## Add New Skills
### The Predict Function
To create a new skill, simply the predict function needs to be implemented. For facilitating this, we provide two packages: [*SQuARE-skill-helpers*](https://github.com/UKP-SQuARE/square-skill-helpers) and [*SQuARE-skill-api](https://github.com/UKP-SQuARE/square-skill-api). The skill-helpers package facilitates the interaction with other SQuARE services, such as Datastores and Models. The skill-api package wraps the final predict function creating an API that can be accessed by SQuARE. Further, it provides dataclasses (pydantic) for input and output of the predict function.

As mentioned above mainly a predict function, defining the pipeline needs to be implemented. 
First, install the required packages:
```bash
pip install git+https://github.com/UKP-SQuARE/square-skill-helpers.git@v0.0.5
pip install git+https://github.com/UKP-SQuARE/square-skill-api.git@v0.0.16 
```
Next, we can implement the `predict` function:
```python3

# import utility classes from `square_skill_api` and `square_skill_helpers`
from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest
from square_skill_helpers import ModelAPI, DataAPI


# create instances of the DataAPI and ModelAPI for interacting with SQuAREs Datastores and Models
data_api = DataAPI()
model_api = ModelAPI()

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
2. Add you skill in the [config.yaml](../config.yaml). Give the skill the same name as the folder under skills. Add your username as author.
3. Once you pull request is approved, your skill url will be `http://<skill-name>`

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
### boolq
*Description*: A categorical QA skill answering boolean questions given a context with yes or no.
*Base-Model*: [bert-base-uncased](https://huggingface.co/bert-base-uncased)
*Adapter*: [AdapterHub/bert-base-uncased-pf-boolq](https://adapterhub.ml/adapters/AdapterHub/bert-base-uncased-pf-boolq/)
*Training Data*: [boolq](https://huggingface.co/datasets/boolq)
*Example*:
Question: 
```
is windows movie maker part of windows essentials
``` 
Context: 
```
Windows Movie Maker (formerly known as Windows Live Movie Maker in Windows 7) is a discontinued video editing software by Microsoft. It is a part of Windows Essentials software suite and offers the ability to create and edit videos as well as to publish them on OneDrive, Facebook, Vimeo, YouTube, and Flickr.
```
### commonsense-qa
*Description*: A multiple-choice QA skill answering commonsense questions by scoring a set of answer candidates.
*Base-Model*: [bert-base-uncased](https://huggingface.co/bert-base-uncased)
*Adapter*: [AdapterHub/bert-base-uncased-pf-commonsense_qa](https://adapterhub.ml/adapters/AdapterHub/bert-base-uncased-pf-commonsense_qa/)
*Training Data*: [CommonsenseQA](https://huggingface.co/datasets/commonsense_qa)
*Example*:
Question
```
Sammy wanted to go to where the people were. Where might he go?
```
Answer Choices
```
race track
populated areas
the desert
apartment
roadblock
```
### squad-v2
*Description*: A extractive QA skill, selecting an answer to a question from a text span of the provided context.
*Base-Model*: [bert-base-uncased](https://huggingface.co/bert-base-uncased)
*Adapter*: [qa/squad2@ukp](https://adapterhub.ml/adapters/ukp/roberta-base_qa_squad2_houlsby/)
*Training Data*: [SQuAD V2.0](https://huggingface.co/datasets/squad_v2)
Question
```
What areas did Beyonce compete in when she was growing up?
```
Context
```
Beyoncé Giselle Knowles-Carter (born September 4, 1981) is an American singer, songwriter, record producer and actress. Born and raised in Houston, Texas, she performed in various singing and dancing competitions as a child, and rose to fame in the late 1990s as lead singer of R&B girl-group Destiny's Child. Managed by her father, Mathew Knowles, the group became one of the world's best-selling girl groups of all time. Their hiatus saw the release of Beyoncé's debut album, Dangerously in Love (2003), which established her as a solo artist worldwide, earned five Grammy Awards and featured the Billboard Hot 100 number-one singles "Crazy in Love" and "Baby Boy".
```
### retrieve-span
*Description*:
*Base-Model*: [DPR](https://huggingface.co/facebook/dpr-question_encoder-single-nq-base) (retrieval); [bert-base-uncased](https://huggingface.co/bert-base-uncased) (span-extraction)
*Adapter*: [qa/squad2@ukp](https://adapterhub.ml/adapters/ukp/roberta-base_qa_squad2_houlsby/)
*Training Data*: [SQuAD V2.0](https://huggingface.co/datasets/squad_v2)
*Example*:
Questions
```
When was TU Darmstadt established?
```

### retrieve-bioasq
*Description*: An open-domain, extractive QA skill, using PubMed articles as background knowledge and span-extraction for answer selection. For retrieval BM25 is used.
*Base-Model*: [bert-base-uncased](https://huggingface.co/bert-base-uncased)
*Adapter*: [qa/squad2@ukp](https://adapterhub.ml/adapters/ukp/roberta-base_qa_squad2_houlsby/)
*Training Data*: [SQuAD V2.0](https://huggingface.co/datasets/squad_v2) (span-extraction)
*Example*:
Question:
```
What are the symptoms of MERS?
```

### exctractive-qa
*Description*: An extractive QA skill that can work with any base-model and adapter (has to be an extractive QA adapter).
### multiple-choice-qa
*Description*: A multiple-choice QA skill that can work with any base-model and adapter (has to be a multiple-choice QA adapter).
