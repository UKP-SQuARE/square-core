# Management Client

This package contains the client to access the model api.

## Example prediction:

A prediction with the ManagementClient can be done with the following method:

`predict(self, model_identifier, prediction_method, input_data)`
Request model prediction.
`model_identifier` (str): the identifier of the model that should be used for the prediction
`prediction_method` (str): what kind of prediction should be made. Possible values are embedding,
                sequence-classification, token-classification, generation, question-answering
`input_data` (Dict): the input for the prediction

So an example call would be:
```
client.predict(identifier, input_data={"input": ["Some text"], "adapter_name": "ner/conll2003@ukp"},
               prediction_method="token-classification")
```

## Building the package
To build the package, first update the version in `setup.py` then run:

```
python setup.py sdist bdist_wheel
```

Now the build package is created in `management_client/dist`. This needs to be uploaded to pypi.
1. Ensure you have installed `twine` (`pip install twine`)
2. Ensure you have a user account on pypi which can update the management client project
3. Upload the pacakage using `twine upload dist/*`

