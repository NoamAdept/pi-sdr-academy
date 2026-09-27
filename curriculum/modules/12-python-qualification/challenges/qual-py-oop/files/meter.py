class SignalMeter:
    def __init__(self):
        self._r=[]
    def add(self, power_db: float) -> None:
        raise NotImplementedError
    def average(self) -> float:
        raise NotImplementedError
