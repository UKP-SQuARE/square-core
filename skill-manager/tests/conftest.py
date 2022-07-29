import jwt
import pytest
from skill_manager.models import Skill, SkillSettings
from testcontainers.mongodb import MongoDbContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="module")
def monkeymodule():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="module")
def init_mongo_db():
    mongo_db = MongoDbContainer("mongo:5.0.4")
    mongo_db.start()
    mongo_db._connect()
    try:
        yield mongo_db
    except Exception as err:
        raise err
    finally:
        mongo_db.stop()


@pytest.fixture(scope="module")
def init_redis():
    redis_password = "redis-pass"
    redis = RedisContainer("redis:latest", password=redis_password)
    redis.start()
    redis._connect()
    try:
        yield redis
    except Exception as err:
        raise err
    finally:
        redis.stop()


@pytest.fixture
def skill_prediction_factory():
    def skill_prediction(**kwargs):
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
                    **kwargs,
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
