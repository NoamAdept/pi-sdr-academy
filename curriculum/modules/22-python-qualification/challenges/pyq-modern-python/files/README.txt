BUILD A TYPED PACKET ROUTER

Complete packet_router.py using modern standard-library Python.

1. Packet must be an immutable (frozen) dataclass with:
   kind: str
   payload: bytes = b""
2. counted must be a type-preserving decorator. Its wrapper:
   - uses functools.wraps
   - starts with wrapper.calls == 0
   - increments calls only after a successful call
3. route must use match/case and return:
   Packet("ping")              -> "PING"
   Packet("data", b"\x01\xaf") -> "DATA:01af"
   Packet("data", b"")         -> "EMPTY"
   any other kind              -> "DROP:<kind>"

Keep route's annotations and docstring intact through decoration.
No packages or downloads are needed. Run `python3 packet_router.py`, then
`./check`.
