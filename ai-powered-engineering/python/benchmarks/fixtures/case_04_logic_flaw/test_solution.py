from solution import apply_discount_tier


def test_twenty_percent_discount():
    assert apply_discount_tier(100.0, 0.20) == 80.0


def test_zero_discount():
    assert apply_discount_tier(50.0, 0.0) == 50.0


def test_full_discount():
    assert apply_discount_tier(75.0, 1.0) == 0.0
