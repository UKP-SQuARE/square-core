import uuid
from unittest.mock import MagicMock

import pytest
from docker import DockerClient
from fastapi.testclient import TestClient
from skill_manager.core.docker_client import SkillManagerDockerClient
from skill_manager.main import app
from skill_manager.models.skill_deployment import SkillDeployment
from skill_manager.core.keycloak_client import KeycloakClient
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


@pytest.mark.parametrize(
    "skill_template_running", [False, True], ids=["not-runnning", "running"]
)
def test_get_deployment_by_id(
    mongo_db, docker_client: DockerClient, skill_template_running
):

    skill_template_id = str(uuid.uuid1())
    sm_docker_client_mock = MagicMock(spec=SkillManagerDockerClient)
    if skill_template_running:
        test_image = "containous/whoami"
        test_url = "http://test.test"
        container = docker_client.containers.run(
            test_image,
            detach=True,
            remove=True,
            labels={"skill-template-id": f"{skill_template_id}", "url": test_url},
        )
    else:
        test_url = None
        container = None
    sm_docker_client_mock.get_skill_template_container_by_id.return_value = container
    app.dependency_overrides[SkillManagerDockerClient] = lambda: sm_docker_client_mock

    with TestClient(app) as test_client:
        response = test_client.get("/api/deployments/{id}".format(id=skill_template_id))
        assert response.status_code == 200
        actual_skill_deployment = SkillDeployment.parse_obj(response.json())
        expected_skill_deployment = SkillDeployment(
            skill_template_id=skill_template_id,
            deployed=skill_template_running,
            url=test_url,
        )
        assert actual_skill_deployment == expected_skill_deployment

    if container:
        container.stop()


@pytest.mark.parametrize("num_containers", [0, 3], ids=["zero-runnning", "n-running"])
def test_get_deployments(
    mongo_db,
    docker_client: DockerClient,
    num_containers,
    token_factory,
    skill_template_factory,
):

    username = "test-user"
    token = token_factory(preferred_username=username)

    sm_docker_client_mock = MagicMock(spec=SkillManagerDockerClient)
    containers = []
    test_image = "containous/whoami"
    test_url = "http://test.test"
    for _ in range(num_containers):
        # create the skill template in mongodb
        with TestClient(app) as test_client:
            skill_template_name = f"test-create-skill-template"
            test_skill_template = skill_template_factory(
                name=skill_template_name, user_id=username
            )
            response = test_client.post(
                "/api/skill-templates",
                data=test_skill_template.json(),
                headers=dict(Authorization="Bearer " + token),
            )
            skill_template_id = response.json()["id"]

        # deploy a container
        container = docker_client.containers.run(
            test_image,
            detach=True,
            remove=True,
            labels={
                "type": "skill-template",
                "skill-template-id": f"{skill_template_id}",
                "url": test_url,
            },
        )
        containers.append(container)
    sm_docker_client_mock.get_skill_template_containers.return_value = containers
    app.dependency_overrides[SkillManagerDockerClient] = lambda: sm_docker_client_mock

    for _ in range(4):
        container = docker_client.containers.run(
            test_image,
            detach=True,
            remove=True,
        )
        containers.append(container)

    with TestClient(app) as test_client:
        response = test_client.get("/api/deployments")
        assert response.status_code == 200, response.content
        assert len(response.json()) == num_containers, response.json()

    for container in containers:
        container.stop()
