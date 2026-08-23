import numpy as np

def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

from build_flowgraph import build_and_run
try:
    tb, sink = build_and_run()
except Exception as exc:
    fail(str(exc))
if len(tb.connections) != 2:
    fail("expected exactly two edges")
if sink.data is None or not np.array_equal(sink.data, [3, 6, 9, 12]):
    fail("sink output is incorrect")
print("CHECK_OK")
