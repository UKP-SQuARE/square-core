import uuid
from unittest.mock import MagicMock

from bson import ObjectId
from fastapi.testclient import TestClient
from skill_manager import mongo_client
from skill_manager.core.keycloak_client import KeycloakClient
from skill_manager.main import app
from skill_manager.routers.skill_templates import auth

keycloak_client_mock = MagicMock()
keycloak_client_mock.create_client.return_value = {
    "clientId": "test-client-id",
    "secret": "test-secret",
}
keycloak_client_override = lambda: keycloak_client_mock

realm = "test-realm"
username = "test-user"
app.dependency_overrides[KeycloakClient] = keycloak_client_override
app.dependency_overrides[auth] = lambda: dict(realm=realm, username=username)


def test_get_skill_by_id(mongo_db, token_factory, skill_template_factory):
    token = token_factory(preferred_username=username)
    skill_template_name = "test-get-skill-template-by-id"
    test_skill_template = skill_template_factory(
        name=skill_template_name, user_id=username
    )

    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/skill-templates",
            data=test_skill_template.json(),
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 201, response.content

        skill_template_id = response.json()["id"]
        response = test_client.get(
            "/api/skill-templates/{id}".format(id=skill_template_id)
        )
        assert response.status_code == 200, response.content

        response = response.json()
        assert response["name"] == skill_template_name


def test_get_skill(mongo_db, token_factory, skill_template_factory):

    token = token_factory(preferred_username=username)
    skill_template_name = "test-get-skill-template"
    test_skill_template = skill_template_factory(
        name=skill_template_name, user_id=username
    )

    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/skill-templates",
            data=test_skill_template.json(),
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 201, response.content

        response = test_client.get("/api/skill-templates")
        assert response.status_code == 200, response.content

        response = response.json()
        assert any(r["name"] == skill_template_name for r in response)


def test_create_skill(mongo_db, token_factory, skill_template_factory):

    token = token_factory(preferred_username=username)
    skill_template_name = "test-create-skill-template"
    test_skill_template = skill_template_factory(
        name=skill_template_name, user_id=username
    )

    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/skill-templates",
            data=test_skill_template.json(),
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 201, response.content

        # check that the skill template exists in mongo db
        response = response.json()
        mongo_skill_template = (
            mongo_client.client.skill_manager.skill_templates.find_one(
                {"_id": ObjectId(response["id"])}
            )
        )
        assert mongo_skill_template["name"] == skill_template_name


def test_update_skill(mongo_db, token_factory, skill_template_factory):

    token = token_factory(preferred_username=username)
    skill_template_name = "test-update-skill-template"
    test_skill_template = skill_template_factory(
        name=skill_template_name, user_id=username
    )

    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/skill-templates",
            data=test_skill_template.json(),
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 201, response.content

        skill_template_id = response.json()["id"]
        updated_skill_template_name = "test-update-skill-template-updated"
        response = test_client.put(
            "/api/skill-templates/{id}".format(id=skill_template_id),
            json={"name": updated_skill_template_name},
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 200, response.content
        assert response.json()["name"] == updated_skill_template_name
        mongo_skill_template = (
            mongo_client.client.skill_manager.skill_templates.find_one(
                {"_id": ObjectId(skill_template_id)}
            )
        )
        assert mongo_skill_template["name"] == updated_skill_template_name


def test_delete_skill(mongo_db, token_factory, skill_template_factory):
    token = token_factory(preferred_username=username)
    skill_template_name = "test-delete-skill-template"
    test_skill_template = skill_template_factory(
        name=skill_template_name, user_id=username
    )

    with TestClient(app) as test_client:
        # create skill template
        response = test_client.post(
            "/api/skill-templates",
            data=test_skill_template.json(),
            headers=dict(Authorization="Bearer " + token),
        )
        assert response.status_code == 201, response.content

        skill_template_id = response.json()["id"]

        response = test_client.delete(
            "/api/skill-templates/{id}".format(id=skill_template_id),
            data=test_skill_template.json(),
            headers=dict(Authorization="Bearer " + token),
        )

        # assert it has been deleted from mongodb
        mongo_skill_template = (
            mongo_client.client.skill_manager.skill_templates.find_one(
                {"_id": ObjectId(skill_template_id)}
            )
        )
        assert mongo_skill_template is None


def test_upload_function(mongo_db, monkeypatch, tmp_path_factory):

    skill_template_id = str(uuid.uuid1())
    filename = f"{skill_template_id}.pickle"
    source_dir = tmp_path_factory.mktemp("source")

    source_path = source_dir / filename
    source_path.write_text(f"{skill_template_id}")

    target_dir = tmp_path_factory.mktemp("target")
    monkeypatch.setenv("FUNCTION_DUMP_DIR", str(target_dir))

    with TestClient(app) as test_client:
        with open(source_path, "rb") as file:
            test_client.post(
                f"/api/skill-templates/{skill_template_id}/upload-function",
                files={"file": file},
            )

        assert (
            open(target_dir / f"{skill_template_id}.pickle", "r").read()
            == skill_template_id
        )
