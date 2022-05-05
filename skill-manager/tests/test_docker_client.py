import os
import time
import uuid
from types import FunctionType
from unittest.mock import MagicMock

import dill as pickle
import docker
import pytest
import requests
from docker import DockerClient
from skill_manager.core.docker_client import SkillManagerDockerClient
from skill_manager.models.skill_template import SkillTemplate


@pytest.fixture()
def genearte_id_and_remove_docker_image():
    skill_template_id = str(uuid.uuid1())
    yield skill_template_id

    if os.path.exists(
        f"./skill_manager/skill-template-docker/{skill_template_id}.pickle"
    ):
        os.remove(skill_template_id)

    docker_client = DockerClient.from_env()
    docker_client.images.remove(f"ukpsquare/skill-template-{skill_template_id}")


@pytest.fixture(scope="module")
def docker_client():
    return DockerClient.from_env()


def test_copy_remove_file(tmp_path_factory):

    skill_template_id = str(uuid.uuid1())
    filename = f"{skill_template_id}.pickle"
    source_dir = tmp_path_factory.mktemp("source")
    target_dir = tmp_path_factory.mktemp("target")

    source = source_dir / filename
    source.write_text("test")

    destination = target_dir / filename

    sm_docker_client = SkillManagerDockerClient()
    with sm_docker_client._copy_remove_file(source=source, destination=destination):
        assert os.path.exists(destination)
    assert not os.path.exists(destination)
    assert os.path.exists(source)


def test_copy_remove_dir_destination(tmp_path_factory):
    skill_template_id = str(uuid.uuid1())
    filename = f"{skill_template_id}.pickle"
    source_dir = tmp_path_factory.mktemp("source")
    target_dir = tmp_path_factory.mktemp("target")

    source = source_dir / filename
    source.write_text("test")

    destination = target_dir

    sm_docker_client = SkillManagerDockerClient()
    with pytest.raises(RuntimeError):
        with sm_docker_client._copy_remove_file(source=source, destination=destination):
            pass


def test_copy_remove_source_not_found(tmp_path_factory):
    skill_template_id = str(uuid.uuid1())
    filename = f"{skill_template_id}.pickle"
    source_dir = tmp_path_factory.mktemp("source")
    target_dir = tmp_path_factory.mktemp("target")

    source = source_dir / filename

    destination = target_dir / filename

    sm_docker_client = SkillManagerDockerClient()
    with pytest.raises(FileNotFoundError):
        with sm_docker_client._copy_remove_file(source=source, destination=destination):
            pass


def test_build_skill_template(
    tmp_path_factory, genearte_id_and_remove_docker_image, docker_client: DockerClient
):

    skill_template_id = genearte_id_and_remove_docker_image
    filename = f"{skill_template_id}.pickle"

    source_dir = tmp_path_factory.mktemp("source")
    pickle_path = source_dir / filename
    pickle_path.write_text("hello world")

    sm_docker_client = SkillManagerDockerClient()
    image = sm_docker_client.build_skill_template(
        pickle_path=pickle_path,
        skill_template_docker_dir="./skill_manager/skill-template-docker",
        skill_template_id=skill_template_id,
    )

    # check that image is available
    docker_client.images.get(image.tags[0])
    docker_client.images.get(f"ukpsquare/skill-template-{skill_template_id}")


@pytest.fixture
def get_network_setup_cleanup(docker_client: DockerClient):

    # setup
    test_network = "square-skill-manager-test-network"
    test_image = "containous/whoami"
    test_name = "test-name"
    network = docker_client.networks.create(test_network)

    # test
    yield test_image, test_name, network

    # clean-up
    try:
        container = docker_client.containers.get(test_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass

    network.remove()


def test_get_network(docker_client: DockerClient, get_network_setup_cleanup):

    test_image, test_name, test_network = get_network_setup_cleanup
    docker_client.images.pull(test_image)

    _ = docker_client.containers.run(
        image=test_image,
        name=test_name,
        detach=True,
        remove=True,
        network=test_network.name,
    )

    sm_docker_client = SkillManagerDockerClient()
    network_of_test_container = sm_docker_client._get_network(
        ref_container_name=test_name
    )

    assert network_of_test_container.id == test_network.id


def test_deploy_skill_template(monkeypatch, tmp_path_factory):
    async def predict(query):
        return {
            "predictions": [
                {
                    "prediction_score": 1,
                    "prediction_output": {
                        "output": f"query={query.query}",
                        "output_score": 2,
                    },
                }
            ]
        }

    skill_template_id = str(uuid.uuid1())
    pickle_path = tmp_path_factory.mktemp("pickle-jar") / f"{skill_template_id}.pickle"

    # https://stackoverflow.com/a/49829760
    pickalbe_predict = FunctionType(predict.__code__, {})
    with open(pickle_path, "wb") as fn:
        pickle.dump(pickalbe_predict, fn)

    sm_docker_client = SkillManagerDockerClient()
    _ = sm_docker_client.build_skill_template(
        pickle_path=pickle_path,
        skill_template_docker_dir="./skill_manager/skill-template-docker",
        skill_template_id=skill_template_id,
    )

    test_client_id = str(uuid.uuid1())
    monkeypatch.setenv("WEB_CONCURRENCY", "1")
    monkeypatch.setenv("VERIFY_SSL", "0")
    monkeypatch.setenv("SQUARE_API_URL", "")
    monkeypatch.setenv("KEYCLOAK_BASE_URL", "")
    monkeypatch.setenv("REALM", "")

    skill_template_mock = MagicMock(spec=SkillTemplate)
    skill_template_mock.id = skill_template_id
    skill_template_mock.client_id = test_client_id

    get_network_mock = MagicMock()
    network_name_mock = MagicMock()
    network_name_mock.name = "bridge"
    get_network_mock.return_value = network_name_mock
    sm_docker_client._get_network = get_network_mock

    test_ref_container = "test-ref-container"
    container = sm_docker_client.deploy_skill_template(
        skill_template=skill_template_mock,
        network_ref_container_name=test_ref_container,
        wait=True,
    )

    assert container.status == "running"

    test_query = "test-query"
    query_url = f"http://localhost:{container.ports['80/tcp'][0]['HostPort']}/query"
    time.sleep(5)  # wait for the application startup
    response = requests.post(query_url, json={"query": test_query})
    assert response.status_code == 200, response.content
    assert (
        response.json()["predictions"][0]["prediction_output"]["output"]
        == f"query={test_query}"
    )

    # clean-up
    container.stop()
    container.remove()
