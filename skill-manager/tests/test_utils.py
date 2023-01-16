from skill_manager.utils import merge_dicts

def test_merge_dicts():
    d1 = {"a": 1}
    d2 = {"b": 2}
    merged_dicts = merge_dicts(d1, d2)
    assert merged_dicts == {"a": 1, "b": 2}

def test_overwrite_merge_dicts():
    d1 = {"a": 1}
    d2 = {"a": 2}
    merged_dicts = merge_dicts(d1, d2)
    assert merged_dicts == {"a": 2}
