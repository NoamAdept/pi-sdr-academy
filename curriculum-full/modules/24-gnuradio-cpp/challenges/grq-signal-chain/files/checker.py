def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

from signal_chain import analyze
try:
    result = analyze()
except Exception as exc:
    fail(str(exc))
if result.get("throttle_rate") != 8000:
    fail("throttle rate should match sample rate")
if abs(result.get("magnitude_mean", 0) - 1.0) > 0.03:
    fail("translated channel magnitude is incorrect")
if abs(result.get("envelope_peak_hz", 0) - 80.0) > 2.5:
    fail("expected an 80 Hz envelope peak")
print("CHECK_OK")
