class SampleFormatError(ValueError):
    """A receiver sample line is malformed."""


class ReceiverSession:
    def __init__(self) -> None:
        self.is_open = False
        self.samples: list[tuple[str, float]] = []
        self.errors: list[str] = []
        self.attempted = 0

    def __enter__(self):
        # YOUR CODE HERE
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        # YOUR CODE HERE: close and do not suppress exceptions.
        pass

    def add(self, sample: tuple[str, float]) -> None:
        if not self.is_open:
            raise RuntimeError("receiver session is closed")
        self.samples.append(sample)


def parse_sample(line: str) -> tuple[str, float]:
    # YOUR CODE HERE: return (station, dbm) or raise SampleFormatError.
    raise NotImplementedError


def collect(lines: list[str]) -> ReceiverSession:
    session = ReceiverSession()
    # YOUR CODE HERE: use with and try/except/else/finally.
    return session


if __name__ == "__main__":
    result = collect(["alpha,-67.5", "broken", "bravo,-51"])
    print(result.samples)
    print("errors:", result.errors, "attempted:", result.attempted)
