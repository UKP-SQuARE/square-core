import os

import pytest
import torch
from model_inference.main import auth, get_app


@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app
