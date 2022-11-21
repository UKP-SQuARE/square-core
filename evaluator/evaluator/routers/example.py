import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, Request
from square_auth.auth import Auth
from square_auth.utils import is_local_deployment

from evaluator import mongo_client
from evaluator.auth_utils import get_example_if_authorized
from evaluator.core import DatasetHandler
from evaluator.keycloak_api import KeycloakAPI
from evaluator.models import Example

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/example")
auth = Auth()


@router.get(
    "/bene/{dataset_name:path}",
    status_code=200,
)
async def bene(
    request: Request,
    dataset_name: str = None,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
):
    dataset_handler.get_dataset(dataset_name)


@router.get(
    "",
    response_model=List[str],
)
async def get_public_stuff():
    """Returns a list of strings."""
    data = [
        "this",
        "comes",
        "from",
        "a",
        "public",
        "endpoint",
        "that",
        "requires",
        "no",
        "authentication",
    ]
    logger.debug("get_public_stuff {data}".format(data=data))
    return data


@router.get(
    "/{id}",
    response_model=Example,
)
async def get_example(request: Request, id: str = None):
    example = await get_example_if_authorized(request, exampleId=id)
    logger.debug("get_example: {example}".format(example=example))
    return example


@router.post(
    "",
    response_model=Example,
    status_code=201,
)
async def create_example(
    request: Request,
    example: Example,
    keycloak_api: KeycloakAPI = Depends(KeycloakAPI),
    token_payload: Dict = Depends(auth),
):
    realm = token_payload["realm"]
    username = token_payload["username"]

    if not is_local_deployment():
        client = keycloak_api.create_client(
            realm=realm, username=username, skill_name=skill.name
        )
    else:
        # In local deployment, we don't have Keycloak, so we just create a dummy client
        client = {
            "clientId": "local",
            "secret": "secret",
        }

    exampleId = mongo_client.client.evaluator.example.insert_one(
        example.mongo()
    ).inserted_id
    example = await get_example(request, exampleId)
    logger.debug("create_example: {example}".format(example=example))

    return example
