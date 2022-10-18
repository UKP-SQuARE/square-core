import pytest


import torch
import os

from main import get_app, auth

@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app
