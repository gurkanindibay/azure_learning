from solution import prune_inactive_sessions


def test_prune_inactive():
    sessions = {"user1": 10, "user2": 55, "user3": 20, "user4": 80}
    pruned = prune_inactive_sessions(sessions, timeout_threshold=30)
    assert pruned == {"user1": 10, "user3": 20}


def test_empty_sessions():
    assert prune_inactive_sessions({}, 30) == {}
