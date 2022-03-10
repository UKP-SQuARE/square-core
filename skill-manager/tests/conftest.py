import jwt
import pytest

@pytest.fixture
def token():
    token = jwt.encode(
        {
            "preferred_username": "test-user", 
            "iss": "https://square.ukp-lab.test/auth/realms/test-realm"
        }, 
        "secret",
        algorithm="HS256"
    )
    return token
