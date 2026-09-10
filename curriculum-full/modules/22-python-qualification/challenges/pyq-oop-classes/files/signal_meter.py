class SignalMeter:
    def __init__(self, name: str):
        # YOUR CODE HERE
        pass

    @property
    def name(self) -> str:
        return self._name

    def add_sample(self, dbm: float) -> None:
        # YOUR CODE HERE
        pass

    def average_dbm(self) -> float:
        # YOUR CODE HERE
        raise NotImplementedError


class CalibratedSignalMeter(SignalMeter):
    def __init__(self, name: str, offset_db: float = 0.0):
        # YOUR CODE HERE
        pass

    @property
    def offset_db(self) -> float:
        return self._offset_db

    @offset_db.setter
    def offset_db(self, value: float) -> None:
        # YOUR CODE HERE: accept only -20.0 <= value <= 20.0.
        pass

    def average_dbm(self) -> float:
        # YOUR CODE HERE
        raise NotImplementedError


if __name__ == "__main__":
    meter = CalibratedSignalMeter("roof antenna", 2.5)
    for sample in (-72, -68, -70):
        meter.add_sample(sample)
    print(f"{meter.name}: {meter.average_dbm():.1f} dBm")
