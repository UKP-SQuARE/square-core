## Package
`
SPARQLWrapper==1.8.4
rdflib==6.1.1
`

## Load json needs to be loaded only once


## prediction.py
L489 https://github.com/UKP-SQuARE/square-skill-api/blob/3a6a6adc01feb1367a5eb83608b4f6d944a3135e/square_skill_api/models/prediction.py#L490
`overwrite_from_model_api_output() missing 1 required positional argument: 'value'`


### incosistent context type 
File "/mnt/beegfs/work/fang/square/skill-env/lib/python3.7/site-packages/square_skill_api/models/prediction.py", line 507, in from_generation
    prediction_documents=[PredictionDocument(document=context)],
  File "pydantic/main.py", line 342, in pydantic.main.BaseModel.__init__
pydantic.error_wrappers.ValidationError: 1 validation error for PredictionDocument
document
  none is not an allowed value (type=type_error.none.not_allowed)

https://github.com/UKP-SQuARE/square-skill-api/blob/3a6a6adc01feb1367a5eb83608b4f6d944a3135e/square_skill_api/models/prediction.py#L478


### lack argument.
File "/mnt/beegfs/work/fang/square/skill-env/lib/python3.7/site-packages/square_skill_api/models/prediction.py", line 507, in from_generation
    prediction_documents=[PredictionDocument(document=context)],
  File "pydantic/main.py", line 342, in pydantic.main.BaseModel.__init__
pydantic.error_wrappers.ValidationError: 1 validation error for Prediction
question
  field required (type=value_error.missing)

https://github.com/UKP-SQuARE/square-skill-api/blob/3a6a6adc01feb1367a5eb83608b4f6d944a3135e/square_skill_api/models/prediction.py#L504

## some sparql don't have results how to process this