import pytest

from starlette.config import environ
API_KEY = "test_key"
API_KEY_HEADER_NAME = "Authorization"
environ["API_KEY"] = API_KEY
environ["API_KEY_HEADER_NAME"] = API_KEY_HEADER_NAME

from main import app


@pytest.fixture()
def test_app():
    return app


@pytest.fixture()
def test_key():
    return API_KEY


@pytest.fixture()
def test_header():
    return API_KEY_HEADER_NAME