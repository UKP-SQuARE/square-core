import json

from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock

import pytest
import responses
from fastapi.testclient import TestClient
from square_skill_api.models.request import QueryRequest
from testcontainers.mongodb import MongoDbContainer

from skill_manager import mongo_client
from skill_manager.keycloak_api import KeycloakAPI
from skill_manager.main import app
from skill_manager.models import Skill, SkillSettings
from skill_manager.routers import client_credentials

keycloak_api_mock = MagicMock()
keycloak_api_mock.create_client.return_value = {
    "clientId": "test-client-id",
    "secret": "test-secret",
}
keycloak_api_override = lambda: keycloak_api_mock
app.dependency_overrides[KeycloakAPI] = keycloak_api_override

app.dependency_overrides[client_credentials] = lambda: "test-token"

client = TestClient(app)


@pytest.fixture(scope="module")
def monkeymodule():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="module")
def init_mongo_db():
    mongo_db_test_container = MongoDbContainer("mongo:5.0.4")
    mongo_db_test_container.start()
    try:
        yield mongo_db_test_container
    except Exception as err:
        raise err
    finally:
        mongo_db_test_container.stop()


@pytest.fixture(scope="module")
def pers_client(monkeymodule, init_mongo_db):
    # connection_url = init_mongo_db.get_connection_url()

    # # HACK: *for MAC* host detection does not work properly when running inside docker
    # # therefore, we set an env variable in the Dockerfile and manually replace
    # # the host. Once the issue below is fixed in testcontainers, this could be removed.
    # # https://github.com/testcontainers/testcontainers-python/issues/43
    # if os.getenv("INSIDE_DOCKER", False) == 1:
    #     lindex = connection_url.index("@") + 1
    #     rindex = max(i for i, v in enumerate(connection_url) if v == ":")
    #     connection_url = (
    #         connection_url[:lindex] + "host.docker.internal" + connection_url[rindex:]
    #     )

    monkeymodule.setenv(
        "MONGO_INITDB_ROOT_USERNAME", init_mongo_db.MONGO_INITDB_ROOT_USERNAME
    )
    monkeymodule.setenv(
        "MONGO_INITDB_ROOT_PASSWORD", init_mongo_db.MONGO_INITDB_ROOT_PASSWORD
    )
    monkeymodule.setenv("MONGO_HOST", init_mongo_db.get_container_host_ip())
    monkeymodule.setenv("MONGO_PORT", init_mongo_db.get_exposed_port(27017))
    with TestClient(app) as client:
        yield client


@pytest.fixture
def skill_prediction_factory():
    def skill_prediction():
        return {
            "predictions": [
                {
                    "prediction_score": 1,
                    "prediction_output": {"output": "answer", "output_score": "1"},
                    "prediction_documents": [
                        {
                            "index": "",
                            "document_id": "",
                            "document": "doc one",
                            "span": None,
                            "url": "",
                            "source": "",
                            "document_score": 0.0,
                        }
                    ],
                }
            ]
        }

    return skill_prediction


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture
def skill_factory():
    def skill_init(
        name="test-skill",
        url="http://test-skill.square:1234",
        skill_type="abstractive",
        skill_settings=SkillSettings(),
        user_id="test-user-id",
        description="skill for testing",
        published=False,
        default_skill_args=None,
        **kwargs,
    ):
        # pass `id` or `created_at` as kwargs to add them explicitly
        skill = Skill(
            name=name,
            url=url,
            skill_type=skill_type,
            skill_settings=skill_settings,
            user_id=user_id,
            description=description,
            published=published,
            default_skill_args=default_skill_args,
            **kwargs,
        )
        if not skill.id:
            del skill.id

        return skill

    yield skill_init


def assert_skills_equal_from_response(skill, response):
    """check if the skill object is equal to the one in the response"""
    skill = skill.dict()
    added_skill = response.json()
    for k in added_skill:
        if k in ["id", "client_id", "client_secret"]:
            # these attributes were created when inserting into mongo/keycloak
            continue
        if k in ["created_at"]:
            added_skill[k] = datetime.fromisoformat(added_skill[k])
            # mongodb does not store timezone and nanoseconds
            skill[k] = skill[k].replace(
                tzinfo=None, microsecond=skill[k].microsecond // 1000 * 1000
            )

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


def test_create_skill(pers_client, skill_factory):

    test_skill = skill_factory()
    response = pers_client.post("/api/skill", data=test_skill.json())
    assert response.status_code == 201

    assert_skills_equal_from_response(test_skill, response)


def test_get_skill_by_id(pers_client, skill_factory):

    test_skill = skill_factory()
    response = pers_client.post("/api/skill", data=test_skill.json())
    added_skill_id = response.json()["id"]

    response = pers_client.get(f"/api/skill/{added_skill_id}")
    assert response.status_code == 200

    assert_skills_equal_from_response(test_skill, response)


def test_get_skill_by_id_token(pers_client: TestClient, skill_factory, token):
    test_skill = skill_factory(user_id="test-user")
    response = pers_client.post("/api/skill", data=test_skill.json())
    added_skill_id = response.json()["id"]

    response = pers_client.get(
        f"/api/skill/{added_skill_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_get_all_skills(pers_client, skill_factory):

    current_user = "current-user"
    public_skill = skill_factory(user_id="another-user", published=True)
    private_skill = skill_factory(user_id="another-user", published=False)
    user_skill = skill_factory(user_id=current_user, published=False)
    skills_to_add = dict(
        public_skill=public_skill, private_skill=private_skill, user_skill=user_skill
    )

    skill_name_to_id = {}
    for skill_name, skill in skills_to_add.items():
        response = pers_client.post("/api/skill", data=skill.json())
        skill_name_to_id[skill_name] = response.json()["id"]

    # test with anonymous user
    response = pers_client.get(f"/api/skill")
    assert response.status_code == 200

    returned_skill_ids = [skill["id"] for skill in response.json()]
    assert skill_name_to_id["public_skill"] in returned_skill_ids
    assert skill_name_to_id["private_skill"] not in returned_skill_ids
    assert skill_name_to_id["user_skill"] not in returned_skill_ids

    # test with registered user
    response = pers_client.get(f"/api/skill", params=dict(user_id=current_user))
    assert response.status_code == 200

    returned_skill_ids = [skill["id"] for skill in response.json()]
    assert skill_name_to_id["public_skill"] in returned_skill_ids
    assert skill_name_to_id["private_skill"] not in returned_skill_ids
    assert skill_name_to_id["user_skill"] in returned_skill_ids


def test_get_public_user_skill_only_once(pers_client, skill_factory):
    """test if a user publised their skill, that GET /skills only returns it once"""

    current_user = "current-user-2"
    skill = skill_factory(user_id=current_user, published=True)

    response = pers_client.post("/api/skill", data=skill.json())
    skill_id = response.json()["id"]

    response = pers_client.get(f"/api/skill", params=dict(user_id=current_user))
    assert response.status_code == 200
    returned_skills = response.json()

    # filter skills by user
    user_skills = list(filter(lambda s: s["user_id"] == current_user, returned_skills))

    assert user_skills[0]["id"] == skill_id
    assert len(user_skills) == 1


def test_update_skill(pers_client, skill_factory):

    test_skill = skill_factory()
    response = pers_client.post("/api/skill", data=test_skill.json())

    skill_id = response.json()["id"]
    test_skill.id = skill_id
    updated_skill_name = "updated skill"
    test_skill.name = updated_skill_name
    response = pers_client.put(
        f"/api/skill/{skill_id}", json=dict(name=updated_skill_name)
    )
    assert response.status_code == 200
    assert response.json()["name"] == updated_skill_name

    assert_skills_equal_from_response(test_skill, response)


def test_delete_skill(pers_client, skill_factory):

    test_skill = skill_factory()
    response = pers_client.post("/api/skill", data=test_skill.json())

    skill_id = response.json()["id"]

    response = pers_client.delete(f"/api/skill/{skill_id}")
    assert response.status_code == 204

    response = pers_client.get(
        f"/api/skill/{skill_id}", params=dict(user_id=test_skill.user_id)
    )
    assert response.status_code == 200
    assert response.json() == None


def test_publish_unpublish(pers_client, skill_factory):

    test_skill = skill_factory()
    response = pers_client.post("/api/skill", data=test_skill.json())
    skill_id = response.json()["id"]

    response = pers_client.post(f"/api/skill/{skill_id}/unpublish")
    assert response.status_code == 201
    unpublished_skill = response.json()
    assert not unpublished_skill["published"], unpublished_skill

    response = pers_client.post(f"/api/skill/{skill_id}/publish")
    assert response.status_code == 201
    published_skill = response.json()
    assert published_skill["published"], published_skill


@responses.activate
def test_query_skill(pers_client, skill_factory, skill_prediction_factory):
    test_skill = skill_factory()
    response = pers_client.post("/api/skill", data=test_skill.json())
    skill_id = response.json()["id"]

    responses.add(
        responses.POST,
        url=f"{test_skill.url}/query",
        json=skill_prediction_factory(),
        status=200,
    )

    query = "a unique query form test_query_skill"
    query_request = QueryRequest(
        query=query,
        user_id="test-user",
        skill_args={"context": "hello"},
        num_results=1,
    )
    response = pers_client.post(
        f"/api/skill/{skill_id}/query", json=query_request.dict()
    )

    assert response.status_code == 200
    saved_prediction = mongo_client.client.skill_manager.predictions.find_one(
        {"query": query}
    )

    TestCase().assertDictEqual(
        response.json(), {"predictions": saved_prediction["predictions"]}
    )


@responses.activate
def test_query_skill_with_default_skill_args(
    pers_client, skill_factory, skill_prediction_factory
):
    default_skill_args = {"adapter": "my-adapter", "context": "default context"}
    test_skill = skill_factory(default_skill_args=default_skill_args)

    response = pers_client.post("/api/skill", data=test_skill.json())
    skill_id = response.json()["id"]

    responses.add(
        responses.POST,
        url=f"{test_skill.url}/query",
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
        f"/api/skill/{skill_id}/query", json=query_request.dict()
    )

    actual_skill_query_body = json.loads(responses.calls[0].request.body)["skill_args"]
    expected_skill_query_body = default_skill_args
    expected_skill_query_body["context"] = query_context["context"]
    TestCase().assertDictEqual(actual_skill_query_body, expected_skill_query_body)
