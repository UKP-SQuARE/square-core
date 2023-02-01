import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and context, performs extractive QA. This skill is a general
    skill, it can be used with any adapter for extractive question answering. The
    adapter to use can be specified in the `skill_args` or via the `default_skill_args`
    in the skill-manager.
    """

    request.query = ["Which NFL team represented the AFC at Super Bowl 50?", "Which NFL team represented the NFC at Super Bowl 50?"]
    request.skill_args["context"] = ["Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title.", "Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title."]
    
    query = request.query
    context = request.skill_args["context"]
    prepared_input = [[query, context]]

    model_request_kwargs = extract_model_kwargs_from_request(request)

    model_request = {"input": prepared_input, **model_request_kwargs}

    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]
        if request.skill_args.get("average_adapters"):
            model_request["model_kwargs"]["average_adapters"] = True

    #model_response = await square_model_client(
    #    model_name=request.skill_args["base_model"],
    #    pipeline="question-answering",
    #    model_request=model_request,
    #)
    model_response = get_model_response()
    logger.info(f"Model response:\n{model_response}")

    return QueryOutput.from_question_answering(
        questions=query, model_api_output=model_response, context=context
    )

def get_model_response():
    return {
        "model_outputs": {
        "start_logits": "k05VTVBZAQB2AHsnZGVzY3InOiAnPGY0JywgJ2ZvcnRyYW5fb3JkZXInOiBGYWxzZSwgJ3NoYXBlJzogKDIsIDcxKSwgfSAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAqwDQtAALhAwTQQQMH97k/Bi1tFwcBfJ8ENzj7Bjfk0wTTG7cAbcDbBix0ewbyIY8EztTvBV7VFwESw7cA6Hc7A3mMAwUNTCcHxEArBrccbwf9iJ8HYLxrBBQ4uwcGyGMGR4hbB8aZBwQW7FsGxJwnB2XwqwVHeRMHFJDjBLA8bwf+WKcHHTRTB9r7+wGTjsMDx9DHBbFLiwHsnGUAFW6e/oBTrwK33HcGdwwPBmMIavfE8u8ATbnTAKpvBQGt1Ar/4arfAteOGwFBg/r9ZCQ3BP9AVwTkuEMHi1VnAC8oQwTOFC8GMrgdAlyqOwIoAgsDrBQrBuC76wFvB6MCDngbB70m/wLvd3sBdr+HAMzE9wYAoH8H6wAnBaEvmwBYm/j/dUErBG5NIwYWJT8F2YkvBX2s7wSJ0UMEmQUDBZWkRwZ/WQsEgXC/B6QlhwQveOsGlv6vASVYMwfSu+MDBBBTBRb8QwVW7GsE5FynByUgtwbukJMGLbzDBD/Yhwb60HME2+EDBg+kewQihFcHnUzDBJ/5GwVdRPcE4lSLB+RoxweynH8Fg6AzBMI/bwHGeNcGQ19nAxNrUP5ch0r+Np/rAU7Eawchr38CYKijAaiwGwSbLz8C0tnVACJn/vzFdmsDpBg3ADPeOP8x0AMFs4AnBdn8HwYXyhr96KvDAhheiwAbd30An3O+/XWFBwI+lAMF2a+nAmsHYwKzt88DY1qvAFHDLwJ0L5sDDyTXB0sgZwaJRBMEUrN3A",
        "end_logits": "k05VTVBZAQB2AHsnZGVzY3InOiAnPGY0JywgJ2ZvcnRyYW5fb3JkZXInOiBGYWxzZSwgJ3NoYXBlJzogKDIsIDcxKSwgfSAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAo2hjFAT5IdwTvLRcFB2SnBHFJNwVObWcEGoyPBWxRgwULQM8FCpDvBJly+wA7PPcEGhSzBmEUSwSa/BsGwYknABVsnwWSsMMEEyibBf8z6wNnxAMGA5SLBNHU8wd0kOMG+xRLBDm8ywTKhM8F3tyPBLqAZwcNx8MALURnBDlkEwcL+y8AWgTbBhYAuwXJdi8D8hdPAcBiuv23lhsDtoPjAVpvewKcpksCCAQvBM/DVv7Ckfr9YXFPAAKXGPXfLwkB7kq3AQ70awTeL9sDOg93AF7yBwDSy9sCC3EXAC/USwK+LicBabH/AUDJBQHvqgsBkaAnBpBQMv7mzssBcORLBDRbrwFFr2sAUKxHBDt3twBZXiMBb+xnAMPHsvxBKK0As3i7B/EVJwYC3M8FoME/BzcVcwfBeP8HCA2LBZGVGwZhJRcH4PPLAcDFHwfh2K8GLnCrBUyEZwXqalcDC9TPBQPUzwY5vMMHz6xPBYqsNwUGqLMHpij7BD5E7wbIcG8HkgDTBnTM3wZw6LMEOwyjBoc8FwZ7wKcFaog/BC0rzwAxnOsFrCDXB1bS/wNho5sDEghC/9FeUwN9w78A6u/PAuJypwOLsBsHWs1nAqpszwH7lqMDRtJO/3IJ3QGEnn8AEMg7BHB32wLxg0sCJOwe/hBzVwNNT3r8sj5e/DEx1wEnD4b+sfdFAdghdwEsWAMHIN5o+ZniqwNGeBsE/3ubAhC3MwHZuFcGaPdzArv9zwCEz+L8wN4K/"
        },
        "model_output_is_encoded": True,
        "answers": [
        [
            {
            "score": 0.8567973375320435,
            "start": 177,
            "end": 191,
            "answer": "Denver Broncos"
            }
        ],
        [
            {
            "score": 0.8632825613021851,
            "start": 249,
            "end": 266,
            "answer": "Carolina Panthers"
            }
        ]
        ],
        "questions": [],
        "contexts": [],
        "attributions": [],
        "adversarial": {
        "indices": []
        }
    }
    
