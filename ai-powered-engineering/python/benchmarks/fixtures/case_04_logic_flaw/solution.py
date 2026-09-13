def apply_discount_tier(price: float, discount: float) -> float:
    """Calculates discounted price. Discount is represented as a decimal fraction (e.g., 0.20 for 20%)."""
    # BUG: Multiplies price by discount directly instead of applying (1 - discount)
    return round(price * discount, 2)
