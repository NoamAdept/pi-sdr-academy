def dbm_to_quality(dbm: int) -> str:
    """Convert a received power reading to a simple quality label."""
    if dbm >= -50:
        return "excellent"
    if dbm >= -80:
        return "usable"
    return "weak"
