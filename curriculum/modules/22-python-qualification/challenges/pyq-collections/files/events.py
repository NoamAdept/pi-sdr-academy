from collections import defaultdict

EVENTS = [
    {"id": "e1", "station": "alpha", "frequency_hz": 100_000_000, "dbm": -55},
    {"id": "e2", "station": "bravo", "frequency_hz": 101_500_000, "dbm": -72},
    {"id": "e3", "station": "alpha", "frequency_hz": 100_000_000, "dbm": -65},
    {"id": "e4", "station": "charlie", "frequency_hz": 99_900_000, "dbm": -48},
    {"id": "e5", "station": "bravo", "frequency_hz": 101_500_000, "dbm": -58},
]


def summarize(events: list[dict]) -> dict:
    """Build a compact summary without changing events."""
    # YOUR CODE HERE
    raise NotImplementedError


if __name__ == "__main__":
    from pprint import pprint
    pprint(summarize(EVENTS))
