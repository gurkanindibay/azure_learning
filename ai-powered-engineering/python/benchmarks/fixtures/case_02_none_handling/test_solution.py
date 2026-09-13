from solution import normalize_user_handle


def test_normal_handle():
    assert normalize_user_handle("  JohnDoe ") == "johndoe"


def test_none_handle():
    assert normalize_user_handle(None) == ""


def test_empty_handle():
    assert normalize_user_handle("") == ""
