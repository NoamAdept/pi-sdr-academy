from dataclasses import dataclass, asdict
import json
@dataclass
class Frame:
    freq_mhz: float
    note: str
def to_json(frame: Frame) -> str:
    raise NotImplementedError
