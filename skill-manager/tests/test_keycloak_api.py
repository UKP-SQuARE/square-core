import json

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError
from testcontainers.core.container import DockerContainer

from skill_manager.keycloak_api import KeycloakAPI
from tests.testcontainer_keycloak import TestcontainerKeycloak


@pytest.fixture(scope="session")
def monkeypatch_session():
    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="session")
def keycloak(monkeypatch_session: MonkeyPatch):
    with TestcontainerKeycloak("jboss/keycloak:16.1.1") as kc:
        monkeypatch_session.setenv("KEYCLOAK_BASE_URL", kc.get_connection_url())
        yield kc


@pytest.fixture(scope="session")
def kc_admin_master(keycloak: DockerContainer):
    return KeycloakAdmin(
        server_url=f"{keycloak.get_connection_url()}/auth/",
        username="admin",
        password="admin",
        realm_name="master",
        verify=True,
    )


@pytest.fixture(scope="session")
def kc_admin_realm_factory(keycloak):
    def kc_realm(realm: str):
        return KeycloakAdmin(
            server_url=f"{keycloak.get_connection_url()}/auth/",
            username="admin",
            password="admin",
            realm_name=realm,
            user_realm_name="master",
            verify=True,
        )

    return kc_realm


@pytest.fixture(scope="session")
def import_test_realm(monkeypatch_session: MonkeyPatch, kc_admin_master: KeycloakAdmin):
    realm_payload = json.load(open("tests/test-realm-export.json", "r"))
    kc_admin_master.import_realm(realm_payload)
    # test-manager and test-manager secret are hard coded into the .json
    monkeypatch_session.setenv("CLIENT_ID", "test-manager")
    monkeypatch_session.setenv("CLIENT_SECRET", "test-manager-secret")


def test_create_client(kc_admin_realm_factory, import_test_realm):
    realm = "test-realm"
    username = "test-user"
    skill_name = "test-skill"

    keycloak_api = KeycloakAPI()
    expected_client = keycloak_api.create_client(
        realm=realm, username=username, skill_name=skill_name
    )

    kc_admin: KeycloakAdmin = kc_admin_realm_factory(realm=realm)
    actual_client = kc_admin.get_client(expected_client["id"])

    assert expected_client["clientId"] == actual_client["clientId"]

    # check if tokens can be obtained for the new client
    response = requests.post(
        f"{keycloak_api.settings.base_url}/auth/realms/{realm}"
        "/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": expected_client["clientId"],
            "client_secret": expected_client["secret"],
        },
    )
    response.raise_for_status()
    token = response.json()["access_token"]


def test_update_client(kc_admin_realm_factory, import_test_realm):
    realm = "test-realm"
    username = "test-user"
    skill_name = "test-skill-update"

    keycloak_api = KeycloakAPI()
    initial_client = keycloak_api.create_client(
        realm=realm, username=username, skill_name=skill_name
    )
    assert initial_client["enabled"]

    updated_client = keycloak_api.update_client(
        realm=realm, client_id=initial_client["clientId"], enabled=False
    )
    assert not updated_client["enabled"]

    kc_admin: KeycloakAdmin = kc_admin_realm_factory(realm=realm)
    actual_client = kc_admin.get_client(initial_client["id"])
    assert not actual_client["enabled"]


def test_delete_client(kc_admin_realm_factory, import_test_realm):
    realm = "test-realm"
    username = "test-user"
    skill_name = "test-skill-delete"

    keycloak_api = KeycloakAPI()
    client = keycloak_api.create_client(
        realm=realm, username=username, skill_name=skill_name
    )
    keycloak_api.delete_client(realm=realm, client_id=client["clientId"])

    kc_admin: KeycloakAdmin = kc_admin_realm_factory(realm=realm)
    with pytest.raises(KeycloakGetError):
        kc_admin.get_client(client["id"])
