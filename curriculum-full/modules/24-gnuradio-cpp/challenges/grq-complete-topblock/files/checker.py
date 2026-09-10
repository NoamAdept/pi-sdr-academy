def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

from complete_topblock import build_and_run
try:
    tb, sink = build_and_run()
except Exception as exc:
    fail(str(exc))
if len(tb.connections) != 4:
    fail("expected a five-block linear chain")
if sink.metrics is None:
    fail("top block was not run")
m = sink.metrics
if abs(m.get("magnitude_mean", 0) - 1.0) > 0.03:
    fail("magnitude metric differs from reference")
if abs(m.get("magnitude_peak_hz", 0) - 80.0) > 2.5:
    fail("spectrum metric differs from reference")
print("CHECK_OK")
