def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

from tagged_flow import transfer
try:
    result = transfer()
except Exception as exc:
    fail(str(exc))
if result.get("secret") != "offsets_are_metadata":
    fail("secret tag missing")
if result.get("items") != [10, 20, 30, 40]:
    fail("stream items changed")
if result.get("messages") != [("status", "done")]:
    fail("message port event missing")
print("CHECK_OK")
