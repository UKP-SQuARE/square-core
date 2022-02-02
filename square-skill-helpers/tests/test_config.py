import os
import pytest
from square_skill_helpers.config import SquareSkillHelpersConfig

@pytest.fixture
def model_api_key(): return "model-api-key"

def test_config_init(model_api_key):
    with pytest.raises(TypeError):
        # missing model api key
        _ = SquareSkillHelpersConfig()

    config = SquareSkillHelpersConfig(model_api_key=model_api_key)
    assert config.model_api_key == model_api_key

def test_config_from_dotenv(tmp_path, model_api_key):
    with pytest.raises(TypeError):
        # missing model api key
        config = SquareSkillHelpersConfig.from_dotenv()

    env_file = tmp_path / ".env"
    with open(env_file, "w") as fh:
        fh.write(f"MODEL_API_KEY={model_api_key}")    
    config = SquareSkillHelpersConfig.from_dotenv(fp=env_file)
    assert config.model_api_key == model_api_key

def test_config_from_dotenv_unknonw_env_file(tmp_path, model_api_key):
    os.environ["MODEL_API_KEY"] = model_api_key
    env_file = tmp_path / ".env"
    with pytest.warns(RuntimeWarning):
        config = SquareSkillHelpersConfig.from_dotenv(fp=env_file)
