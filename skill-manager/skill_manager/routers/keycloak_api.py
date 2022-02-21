import string
import secrets
from typing import Dict

import requests


class KeycloakAPI:
    def __init__(self, keycloak_base_url: str, client_id: str, client_secret: str):
        """Class for interacting with Keycloak for CRUD clients.

        Args:
            keycloak_base_url (str): host and port of the keycloak instance
            client_id (str): client id of the client that is authorized to manage clients
            client_secret (str): client secret
        """
        self.keycloak_base_url = keycloak_base_url
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self, realm: str) -> str:
        """Returns an access token for managing clients in the realm."

        Args:
            realm (str): Realm in which the access token will be allwed to manage clients

        Returns:
            str: access token
        """
        response = requests.post(
            f"{self.keycloak_base_url}"
            f"/auth/realms/{realm}/protocol/openid-connect/token",
            data=dict(
                grant_type="client_credentials",
                client_id=self.client_id,
                client_secret=self.client_secret,
            ),
        )
        response.raise_for_status()

        return response.json()["access_token"]

    def create_client(
        self, realm: str, username: str, skill_name: str, **kwargs
    ) -> Dict:
        """Creates a new client in Keycloak in the provided realm. Client Id will be created from the username and skill_name.

        Args:
            realm (str): Realm where the client will be registered. 
            username (str): User creating the client.
            skill_name (str): Name of the skill this client will be registered for.

        Returns:
            Dict: Created client information in Keycloak.
        """
        access_token = self.get_token()

        secret = self._generate_secret()
        client_id = f"{username}-{skill_name}"

        response = requests.post(
            f"{self.keycloak_base_url}/auth/admin/realms/{realm}"
            f"/clients-registrations/default",
            headers=dict(Authorization=f"Bearer {access_token}"),
            data=dict(
                clientId=client_id,
                secret=secret,
                implicitFlowEnabled=False,
                standardFlowEnabled=False,
                serviceAccountsEnabled=True,
                publicClient=False,
                **kwargs,
            ),
        )

        response.raise_for_status()

        return dict(
            **response.json(),
            secret=secret,
        )

    def update_client(self,  realm: str, client_id: str,**kwargs: Dict) -> Dict:
        """Updates an existing client in Keycloak.

        Args:
            realm (str): The realm of the client.
            client_id (str): The client_id of the client to update
            kwargs (Dict): Any keyword arguments will be passed to the PUT request. For example, a new `secret` can be set this way.

        Returns:
            Dict: Updated client information in Keycloak.
        """
        access_token = self.get_token()

        response = requests.put(
            f"{self.keycloak_base_url}/auth/admin/realms/{realm}"
            f"/clients-registrations/default/{client_id}",
            headers=dict(Authorization=f"Bearer {access_token}"),
            data=dict(**kwargs),
        )

        response.raise_for_status()

        return response.json()

    def delete_client(self, realm: str, client_id: str):
        """Delets an existing client.

        Args:
            realm (str): The realm of the client.
            client_id (str): The client_id of the client to update

        Returns:
            _type_: _description_
        """
        access_token = self.get_token()

        response = requests.delete(
            f"{self.keycloak_base_url}/auth/admin/realms/{realm}"
            f"/clients-registrations/default/{client_id}",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def _generate_secret(length: int = 20) -> str:
        """Generates a random string from ascii letters and digits of lenght `length`.

        Args:
            length (int, optional): Length of the string to genreate. Defaults to 20.

        Returns:
            str: string of length `length`.
        """
        alphabet = string.ascii_letters + string.digits
        secret = "".join(secrets.choice(alphabet) for _ in range(length))

        return secret
