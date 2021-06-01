import pytest
from squareapi.skill.skill_selector import SkillSelector


@pytest.fixture
def skill_selector():
    return SkillSelector()

def test_skill_selector(skill_selector: SkillSelector):
    assert len(skill_selector.skills) == 0
