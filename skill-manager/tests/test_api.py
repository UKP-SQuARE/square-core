import json
import uuid
from unittest import TestCase
from unittest.mock import MagicMock

import pytest
import responses
from fastapi.testclient import TestClient
from square_skill_api.models.request import QueryRequest
from testcontainers.mongodb import MongoDbContainer
from testcontainers.redis import RedisContainer

from skill_manager import mongo_client
from skill_manager.core.model_management_client import ModelManagementClient
from skill_manager.keycloak_api import KeycloakAPI
from skill_manager.main import app
from skill_manager.routers import client_credentials
from skill_manager.routers.skill import auth

keycloak_api_mock = MagicMock()
keycloak_api_mock.create_client.return_value = {
    "clientId": "test-client-id",
    "secret": "test-secret",
}
keycloak_api_override = lambda: keycloak_api_mock
app.dependency_overrides[KeycloakAPI] = keycloak_api_override

app.dependency_overrides[client_credentials] = lambda: "test-token"

mock_model_management_client = lambda: MagicMock()
app.dependency_overrides[ModelManagementClient] = mock_model_management_client

client = TestClient(app)


@pytest.fixture(scope="module")
def pers_client(
    monkeymodule, init_mongo_db: MongoDbContainer, init_redis: RedisContainer
):
    monkeymodule.setenv(
        "MONGO_INITDB_ROOT_USERNAME", init_mongo_db.MONGO_INITDB_ROOT_USERNAME
    )
    monkeymodule.setenv(
        "MONGO_INITDB_ROOT_PASSWORD", init_mongo_db.MONGO_INITDB_ROOT_PASSWORD
    )
    monkeymodule.setenv("MONGO_HOST", init_mongo_db.get_container_host_ip())
    monkeymodule.setenv("MONGO_PORT", init_mongo_db.get_exposed_port(27017))

    monkeymodule.setenv("REDIS_USER", "default")
    monkeymodule.setenv("REDIS_PASSWORD", init_redis.password)
    monkeymodule.setenv("REDIS_HOST", init_redis.get_container_host_ip())
    monkeymodule.setenv(
        "REDIS_PORT", init_redis.get_exposed_port(init_redis.port_to_expose)
    )

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def create_skill_via_api():
    def _create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username="test-user",
        realm="test-realm",
        **skill_kwargs,
    ):
        skill = skill_factory(**{"user_id": username, **skill_kwargs})
        token = token_factory(preferred_username=username)
        app.dependency_overrides[auth] = lambda: dict(realm=realm, username=username)
        response = pers_client.post(
            "/api/skill",
            data=skill.json(),
            headers=dict(Authorization="Bearer " + token),
        )
        return response, skill

    return _create_skill_via_api


def assert_skills_equal_from_response(skill, response):
    """check if the skill object is equal to the one in the response"""
    skill = skill.dict()
    added_skill = response.json()
    for k in added_skill:
        if k in ["id", "client_id", "client_secret", "created_at"]:
            # these attributes were created when inserting into mongo/keycloak
            continue

        assert (
            added_skill[k] == skill[k]
        ), f"added_skill={added_skill[k]} skill={skill[k]}"


def test_heartbeat(client):
    response = client.get("/api/health/heartbeat")
    assert response.status_code == 200
    assert response.json() == {"is_alive": True}


@pytest.mark.parametrize("is_alive", (True, False), ids=["alive", "dead"])
@responses.activate
def test_skill_heartbeat(is_alive, client):
    skill_url = "http://test_skill_url"
    responses.add(
        responses.GET,
        url=f"{skill_url}/health/heartbeat",
        json={"is_alive": True},
        status=200 if is_alive else 404,
    )
    response = client.get(
        "/api/health/skill-heartbeat", params={"skill_url": skill_url}
    )

    assert response.status_code == 200
    assert response.json() == {"is_alive": is_alive}


def test_skill_types(client):
    response = client.get("/api/skill-types")
    assert response.status_code == 200

    skill_types = response.json()
    assert isinstance(skill_types, list), type(skill_types)


@pytest.mark.asyncio
async def test_create_skill(pers_client: TestClient, skill_factory, token_factory):
    test_user = "test-user"
    app.dependency_overrides[auth] = lambda: dict(
        realm="test-realm", username=test_user
    )

    test_skill = skill_factory(user_id=test_user)
    token = token_factory(preferred_username=test_user)

    response = pers_client.post(
        "/api/skill",
        data=test_skill.json(),
        headers=dict(Authorization="Bearer " + token),
    )
    assert response.status_code == 201, response.content

    assert_skills_equal_from_response(test_skill, response)


@pytest.mark.asyncio
async def test_create_skill_with_data_sets(
    pers_client: TestClient, skill_factory, token_factory
):
    test_user = "test-user"
    app.dependency_overrides[auth] = lambda: dict(
        realm="test-realm", username=test_user
    )

    test_skill = skill_factory(user_id=test_user, data_sets=["SQuAD", "HotpotQA"])
    token = token_factory(preferred_username=test_user)

    response = pers_client.post(
        "/api/skill",
        data=test_skill.json(),
        headers=dict(Authorization="Bearer " + token),
    )
    assert response.status_code == 201, response.content

    assert_skills_equal_from_response(test_skill, response)


@pytest.mark.parametrize("published", [True, False], ids=["published", "private"])
def test_get_skill_by_id_authorized(
    published, pers_client, skill_factory, token_factory, create_skill_via_api
):
    test_user = "test-user"
    response, skill = create_skill_via_api(
        pers_client, token_factory, skill_factory, username=test_user, published=True
    )
    added_skill_id = response.json()["id"]

    token = token_factory(preferred_username=test_user)
    response = pers_client.get(
        f"/api/skill/{added_skill_id}", headers=dict(Authorization="Bearer " + token)
    )
    assert response.status_code == 200

    assert_skills_equal_from_response(skill, response)


def test_get_skill_by_id_unauthorized(
    pers_client, skill_factory, token_factory, create_skill_via_api
):
    # create a private skill for skill_creator_user
    skill_creator_user = "skill-creator"
    response, _ = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=skill_creator_user,
        published=False,
    )
    added_skill_id = response.json()["id"]

    test_user = "test-user"
    test_user_token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(
        realm="test-realm", username=test_user
    )

    response = pers_client.get(
        f"/api/skill/{added_skill_id}",
        headers=dict(Authorization="Bearer " + test_user_token),
    )
    assert response.status_code == 403


def test_get_all_skills(
    pers_client, skill_factory, token_factory, create_skill_via_api
):
    test_user = "test-user"
    skill_creator_user = "skill-creator"

    skill_name_to_id = {}
    for skill_type in ["public", "private", "user"]:
        if skill_type == "public":
            username, published = skill_creator_user, True
        elif skill_type == "private":
            username, published = skill_creator_user, False
        elif skill_type == "user":
            username, published = test_user, False
        response, skill = create_skill_via_api(
            pers_client,
            token_factory,
            skill_factory,
            username=username,
            published=published,
        )
        skill_name_to_id[skill_type] = response.json()["id"]

    # test with anonymous user
    response = pers_client.get(f"/api/skill")
    assert response.status_code == 200

    returned_skill_ids = [skill["id"] for skill in response.json()]
    assert skill_name_to_id["public"] in returned_skill_ids
    assert skill_name_to_id["private"] not in returned_skill_ids
    assert skill_name_to_id["user"] not in returned_skill_ids

    # test with registered user
    token = token_factory(preferred_username=test_user)
    response = pers_client.get(
        f"/api/skill", headers=dict(Authorization="Bearer " + token)
    )
    assert response.status_code == 200

    returned_skill_ids = [skill["id"] for skill in response.json()]
    assert skill_name_to_id["public"] in returned_skill_ids
    assert skill_name_to_id["private"] not in returned_skill_ids
    assert skill_name_to_id["user"] in returned_skill_ids


def test_get_public_user_skill_only_once(
    pers_client, skill_factory, token_factory, create_skill_via_api
):
    """test if a user published their skill, that GET /skills only returns it once"""

    test_user = "test-user"
    response, _ = create_skill_via_api(
        pers_client, token_factory, skill_factory, username=test_user, published=True
    )
    skill_id = response.json()["id"]

    token = token_factory(preferred_username=test_user)
    response = pers_client.get(
        f"/api/skill", headers=dict(Authorization="Bearer " + token)
    )
    assert response.status_code == 200
    returned_skills = response.json()

    # filter skills by user
    skill_ids = [skill["id"] for skill in returned_skills]
    assert sorted(skill_ids) == sorted(set(skill_ids))


@pytest.mark.parametrize(
    "authorized", [True, False], ids=["authorized", "unauthorized"]
)
def test_update_skill(
    authorized, pers_client, skill_factory, token_factory, create_skill_via_api
):
    test_realm = "test-realm"
    test_user = "test-user"
    skill_creator = test_user if authorized else "skill-creator"
    response, skill = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=skill_creator,
        published=True,
    )
    skill_id = response.json()["id"]

    skill.id = skill_id
    updated_skill_name = "updated skill"
    skill.name = updated_skill_name

    token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(realm=test_realm, username=test_user)
    response = pers_client.put(
        f"/api/skill/{skill_id}",
        json=dict(name=updated_skill_name),
        headers=dict(Authorization="Bearer " + token),
    )
    if authorized:
        assert response.status_code == 200
        assert response.json()["name"] == updated_skill_name
        assert_skills_equal_from_response(skill, response)
    else:
        assert response.status_code == 403


@pytest.mark.parametrize(
    "authorized", [True, False], ids=["authorized", "unauthorized"]
)
def test_delete_skill(
    authorized, pers_client, skill_factory, token_factory, create_skill_via_api
):
    test_realm = "test-realm"
    test_user = "test-user"
    skill_creator = test_user if authorized else "skill-creator"
    response, _ = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=skill_creator,
        published=True,
    )
    skill_id = response.json()["id"]

    token = token_factory(preferred_username=test_user)
    response = pers_client.delete(
        f"/api/skill/{skill_id}", headers=dict(Authorization="Bearer " + token)
    )

    if authorized:
        assert response.status_code == 204

        response = pers_client.get(
            f"/api/skill/{skill_id}", headers=dict(Authorization="Bearer " + token)
        )
        assert response.status_code == 404
    else:
        assert response.status_code == 403
        token = token_factory(preferred_username=skill_creator)
        app.dependency_overrides[auth] = lambda: dict(
            realm=test_realm, username=skill_creator
        )
        response = pers_client.get(
            f"/api/skill/{skill_id}", headers=dict(Authorization="Bearer " + token)
        )
        assert response.status_code == 200
        assert response.json()["id"] == skill_id


@pytest.mark.parametrize(
    "authorized", [True, False], ids=["authorized", "unauthorized"]
)
def test_publish_unpublish(
    authorized, pers_client, skill_factory, token_factory, create_skill_via_api
):
    test_realm = "test-realm"
    test_user = "test-user"
    skill_creator = test_user if authorized else "skill-creator"

    response, _ = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=skill_creator,
        published=True,
    )
    skill_id = response.json()["id"]

    # appempt publishing/unpublihsing it
    token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(realm=test_realm, username=test_user)
    response = pers_client.post(
        f"/api/skill/{skill_id}/unpublish",
        headers=dict(Authorization="Bearer " + token),
    )
    if authorized:
        assert response.status_code == 201
        unpublished_skill = response.json()
        assert not unpublished_skill["published"]
    else:
        assert response.status_code == 403

    if authorized:
        response = pers_client.post(
            f"/api/skill/{skill_id}/publish",
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 201
        published_skill = response.json()
        assert published_skill["published"]
    else:
        assert response.status_code == 403


@responses.activate
@pytest.mark.parametrize(
    "authorized", [True, False], ids=["authorized", "unauthorized"]
)
def test_query_skill(
    authorized,
    pers_client,
    skill_factory,
    skill_prediction_factory,
    token_factory,
    create_skill_via_api,
):
    test_realm = "test-realm"
    test_user = "test-user"
    skill_creator = test_user if authorized else "skill-creator"
    response, skill = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=skill_creator,
        published=False,
    )

    skill_id = response.json()["id"]

    responses.add(
        responses.POST,
        url=f"{skill.url}/query",
        json=skill_prediction_factory(),
        status=200,
    )

    query = "a unique query form test_query_skill " + str(uuid.uuid1())
    query_request = QueryRequest(
        query=query,
        user_id="test-user",
        skill_args={"context": "hello"},
        num_results=1,
    )
    token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(realm=test_realm, username=test_user)
    response = pers_client.post(
        f"/api/skill/{skill_id}/query",
        json=query_request.dict(),
        headers=dict(Authorization="Bearer " + token),
    )
    if authorized:
        assert response.status_code == 200
        saved_prediction = mongo_client.client.skill_manager.predictions.find_one(
            {"query": query}
        )

        response = response.json()
        # HACK: remove attributions/prediction_graph from repsonse since the object
        # saved in mongo does not contain it because it is "unset" and we remove all
        # unset values when creating the mongo object
        response.pop("adversarial")
        for p in response["predictions"]:
            p.pop("attributions")
            p.pop("prediction_graph")
            p.pop("skill_id")
            p.pop("bertviz")

        TestCase().assertDictEqual(
            response, {"predictions": saved_prediction["predictions"]}
        )
    else:
        assert response.status_code == 403


@responses.activate
def test_query_skill_with_default_skill_args(
    pers_client,
    skill_factory,
    skill_prediction_factory,
    token_factory,
    create_skill_via_api,
):
    test_realm = "test-realm"
    test_user = "test-user"
    default_skill_args = {
        "adapter": "my-adapter",
        "context": "default context",
        "model_kwargs": {"model_foo": "model_bar"},
    }
    response, skill = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=test_user,
        published=False,
        default_skill_args=default_skill_args,
    )

    token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(realm=test_realm, username=test_user)
    response = pers_client.post(
        "/api/skill", data=skill.json(), headers=dict(Authorization="Bearer " + token)
    )
    skill_id = response.json()["id"]

    responses.add(
        responses.POST,
        url=f"{skill.url}/query",
        json=skill_prediction_factory(),
        status=200,
    )

    query_context = {"context": "hello"}
    query_request = QueryRequest(
        query="query",
        user_id="test-user",
        skill_args=query_context,
        num_results=1,
    )
    response = pers_client.post(
        f"/api/skill/{skill_id}/query",
        json=query_request.dict(),
        headers=dict(Authorization="Bearer " + token),
    )

    actual_request_body = json.loads(responses.calls[0].request.body)

    # model_kwargs is supposed to be removed from the skill_args and parsed separately
    TestCase().assertDictEqual(
        actual_request_body["model_kwargs"], default_skill_args.pop("model_kwargs")
    )

    # remaining args should end up in skill_args
    expected_skill_query_body = default_skill_args
    expected_skill_query_body["context"] = query_context["context"]
    TestCase().assertDictEqual(
        actual_request_body["skill_args"], expected_skill_query_body
    )


@responses.activate
def test_query_skill_with_attributions(
    pers_client,
    skill_factory,
    skill_prediction_factory,
    token_factory,
    create_skill_via_api,
):
    test_realm = "test-realm"
    test_user = "test-user"
    default_skill_args = {"adapter": "my-adapter", "context": "default context"}
    response, skill = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=test_user,
        published=False,
        default_skill_args=default_skill_args,
    )

    token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(realm=test_realm, username=test_user)
    response = pers_client.post(
        "/api/skill", data=skill.json(), headers=dict(Authorization="Bearer " + token)
    )
    skill_id = response.json()["id"]

    attributions = {
        "topk_question_idx": [0, 1, 2],
        "topk_context_idx": [0, 1],
        "question_tokens": [[0, "how", 0.2], [1, "are", 0.3], [2, "you", 0.5]],
        "context_tokens": [[0, "hello", 0.2], [1, "world", 0.8]],
    }

    responses.add(
        responses.POST,
        url=f"{skill.url}/query",
        json=skill_prediction_factory(attributions=attributions),
        status=200,
    )

    query_context = {"context": "hello"}
    query_request = QueryRequest(
        query="query",
        user_id="test-user",
        skill_args=query_context,
        num_results=1,
    )
    response = pers_client.post(
        f"/api/skill/{skill_id}/query",
        json=query_request.dict(),
        headers=dict(Authorization="Bearer " + token),
    )
    assert response.status_code == 200

    response = response.json()
    TestCase().assertDictEqual(response["predictions"][0]["attributions"], attributions)


@responses.activate
def test_query_skill_with_cache(
    pers_client,
    skill_factory,
    skill_prediction_factory,
    token_factory,
    create_skill_via_api,
):
    test_realm = "test-realm"
    test_user = "test-user"
    default_skill_args = {"adapter": "my-adapter", "context": "default context"}
    response, skill = create_skill_via_api(
        pers_client,
        token_factory,
        skill_factory,
        username=test_user,
        published=False,
        default_skill_args=default_skill_args,
    )

    token = token_factory(preferred_username=test_user)
    app.dependency_overrides[auth] = lambda: dict(realm=test_realm, username=test_user)
    response = pers_client.post(
        "/api/skill", data=skill.json(), headers=dict(Authorization="Bearer " + token)
    )
    skill_id = response.json()["id"]

    query_context = {"context": "hello"}
    query_request = QueryRequest(
        query="query",
        user_id="test-user",
        skill_args=query_context,
        num_results=1,
    )

    # define the first response of the skill
    prediction_output = {"output": "answer-1", "output_score": "1"}
    responses.add(
        responses.POST,
        url=f"{skill.url}/query",
        json=skill_prediction_factory(prediction_output=prediction_output),
        status=200,
    )
    response_1 = pers_client.post(
        f"/api/skill/{skill_id}/query",
        json=query_request.dict(),
        headers=dict(Authorization="Bearer " + token),
    )

    # update the response
    updateded_output = "updated_output"
    prediction_output = {"output": updateded_output, "output_score": "1"}
    responses.add(
        responses.POST,
        url=f"{skill.url}/query",
        json=skill_prediction_factory(prediction_output=prediction_output),
        status=200,
    )
    response_2 = pers_client.post(
        f"/api/skill/{skill_id}/query",
        json=query_request.dict(),
        headers=dict(Authorization="Bearer " + token),
    )
    # response 1 and 2 should be equal, bc the response was cached on the second request
    assert (
        response_1.json()["predictions"][0]["prediction_output"]["output"]
        == response_2.json()["predictions"][0]["prediction_output"]["output"]
    )

    # add no-cache Header to avoid reading from cache
    response_3 = pers_client.post(
        f"/api/skill/{skill_id}/query",
        json=query_request.dict(),
        headers={"Authorization": "Bearer " + token, "Cache-Control": "no-cache"},
    )
    assert (
        response_3.json()["predictions"][0]["prediction_output"]["output"]
        == updateded_output
    )
