def merge_dicts(*dicts):
    """Merge multiple dictionaries into one. Overwrites values from left to right."""
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged
