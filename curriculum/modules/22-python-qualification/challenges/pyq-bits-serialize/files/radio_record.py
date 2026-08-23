from dataclasses import asdict, dataclass
import json
import struct

FORMAT = ">2sBBI18s"
XOR_KEY = 0x5A
RAW_RECORD = bytes.fromhex(
    "5051010508ac27602a232b0538332e2905293f28333b3633203f"
)


class RecordError(ValueError):
    """The binary radio record is invalid."""


@dataclass(frozen=True)
class RadioRecord:
    version: int
    active: bool
    locked: bool
    calibrated: bool
    center_hz: int
    flag_field: str

    def to_json(self) -> str:
        # YOUR CODE HERE: return deterministic JSON with sorted keys.
        raise NotImplementedError


def decode_status(status: int) -> tuple[bool, bool, bool]:
    """Return active, locked, and calibrated bits."""
    # YOUR CODE HERE: use &, <<, and boolean conversion.
    raise NotImplementedError


def parse_record(data: bytes) -> RadioRecord:
    # YOUR CODE HERE: validate length, magic, version, and UTF-8 payload.
    raise NotImplementedError


def pack_record(record: RadioRecord) -> bytes:
    # YOUR CODE HERE: rebuild the status byte and XOR-encoded payload.
    raise NotImplementedError


if __name__ == "__main__":
    decoded = parse_record(RAW_RECORD)
    print(decoded.to_json())
    print("recovered field:", decoded.flag_field)
