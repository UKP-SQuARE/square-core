import jwt
import pytest

@pytest.fixture
def token_factory():
    def token(**kwargs):
        return jwt.encode(
            {
                "iss": "https://square.ukp-lab.test/auth/realms/test-realm",
                **kwargs
            },
            "secret",
            algorithm="HS256"
        )
    return token
