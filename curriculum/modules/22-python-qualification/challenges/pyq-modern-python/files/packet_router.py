from dataclasses import dataclass
from functools import wraps
from typing import Callable, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


# YOUR CODE HERE: make Packet a frozen dataclass.
class Packet:
    kind: str
    payload: bytes = b""


def counted(func: Callable[P, R]) -> Callable[P, R]:
    """Decorate func and expose the number of successful calls as .calls."""
    # YOUR CODE HERE
    raise NotImplementedError


@counted
def route(packet: Packet) -> str:
    """Return the receiver action for one packet."""
    # YOUR CODE HERE: use match/case and a guard.
    raise NotImplementedError


if __name__ == "__main__":
    for item in (Packet("ping"), Packet("data", b"\x01\xaf"), Packet("other")):
        print(route(item))
    print("successful calls:", route.calls)
