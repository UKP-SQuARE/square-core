import pytest
from model_manager.main import get_app, auth
from dotenv import load_dotenv
import os
from huggingface_hub import HfApi

@pytest.fixture()
def hf_token():
    load_dotenv()
    return os.getenv("HF_TOKEN")

@pytest.fixture
def model_params(request, hf_token):
    api = HfApi()

    try:
        # remove repo if it already exists 
        api.delete_repo(
            token=hf_token,
            repo_id=request.param[0]
        )
    except:
        pass

    return request.param

@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app