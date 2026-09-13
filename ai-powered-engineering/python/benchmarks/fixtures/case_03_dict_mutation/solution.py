def prune_inactive_sessions(data: dict, timeout_threshold: int) -> dict:
    """Removes sessions with idle time exceeding threshold."""
    # BUG: Modifies dictionary directly while iterating
    for k, v in data.items():
        if v > timeout_threshold:
            del data[k]
    return data
