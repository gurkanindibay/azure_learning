def normalize_user_handle(text: str | None) -> str:
    """Cleans up and standardizes a user handle."""
    # BUG: Fails when text is None
    return text.strip().lower()  # type: ignore
