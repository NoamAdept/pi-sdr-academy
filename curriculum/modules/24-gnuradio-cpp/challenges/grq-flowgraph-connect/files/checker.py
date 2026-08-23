from pathlib import Path
import os
import numpy as np

def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

from connect_flowgraph import build_and_run
try:
    tb, sink = build_and_run()
except Exception as exc:
    fail(str(exc))
if len(tb.connections) != 4:
    fail("expected four port-to-port edges")
got = None if sink.data is None else bytes(np.rint(sink.data).astype("uint8"))
# Vector math yields the ASCII prefix of the curriculum flag.
if got != b"flag{w":
    fail("sink text/hash prefix is incorrect")
print("CHECK_OK")
