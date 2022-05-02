import jwt
import pytest
from fastapi.testclient import TestClient
from testcontainers.mongodb import MongoDbContainer

from skill_manager.main import app
from skill_manager.models.skill import Skill, SkillSettings


@pytest.fixture(scope="module")
def monkeymodule():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="module")
def mongo_db(monkeymodule):
    mongo_db_test_container = MongoDbContainer("mongo:5.0.4")
    mongo_db_test_container.start()
    monkeymodule.setenv(
        "MONGO_INITDB_ROOT_USERNAME", mongo_db_test_container.MONGO_INITDB_ROOT_USERNAME
    )
    monkeymodule.setenv(
        "MONGO_INITDB_ROOT_PASSWORD", mongo_db_test_container.MONGO_INITDB_ROOT_PASSWORD
    )
    monkeymodule.setenv("MONGO_HOST", mongo_db_test_container.get_container_host_ip())
    monkeymodule.setenv("MONGO_PORT", mongo_db_test_container.get_exposed_port(27017))
    try:
        yield mongo_db_test_container
    except Exception as err:
        raise err
    finally:
        mongo_db_test_container.stop()


@pytest.fixture(scope="module")
def pers_client(mongo_db) -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def skill_prediction_factory():
    def skill_prediction():
        return {
            "predictions": [
                {
                    "prediction_score": 1,
                    "prediction_output": {"output": "answer", "output_score": "1"},
                    "prediction_documents": [
                        {
                            "index": "",
                            "document_id": "",
                            "document": "doc one",
                            "span": None,
                            "url": "",
                            "source": "",
                            "document_score": 0.0,
                        }
                    ],
                }
            ]
        }

    return skill_prediction


@pytest.fixture
def skill_factory():
    def skill_init(
        name="test-skill",
        url="http://test-skill.square:1234",
        skill_type="abstractive",
        skill_settings=SkillSettings(),
        user_id="test-user-id",
        description="skill for testing",
        published=False,
        default_skill_args=None,
        **kwargs,
    ):
        # pass `id` or `created_at` as kwargs to add them explicitly
        skill = Skill(
            name=name,
            url=url,
            skill_type=skill_type,
            skill_settings=skill_settings,
            user_id=user_id,
            description=description,
            published=published,
            default_skill_args=default_skill_args,
            **kwargs,
        )
        if not skill.id:
            del skill.id

        return skill

    yield skill_init


@pytest.fixture
def token_factory():
    def token(**kwargs):
        return jwt.encode(
            {"iss": "https://square.ukp-lab.test/auth/realms/test-realm", **kwargs},
            "secret",
            algorithm="HS256",
        )

    return token
