def calculate_running_deltas(items: list[float]) -> list[float]:
    """Calculates deltas between adjacent items."""
    deltas = []
    # BUG: off-by-one error (range goes 1 past the valid index)
    for i in range(len(items) + 1):
        delta = items[i + 1] - items[i]
        deltas.append(delta)
    return deltas
