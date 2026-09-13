from solution import calculate_running_deltas


def test_empty_list():
    assert calculate_running_deltas([]) == []


def test_single_element():
    assert calculate_running_deltas([10.0]) == []


def test_multiple_elements():
    assert calculate_running_deltas([1.0, 3.0, 6.0, 10.0]) == [2.0, 3.0, 4.0]
