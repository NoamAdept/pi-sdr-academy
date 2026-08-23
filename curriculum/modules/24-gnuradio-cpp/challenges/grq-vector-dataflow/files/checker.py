def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

from vector_flow import recover
try:
    result = recover()
except Exception as exc:
    fail(str(exc))
if result.get("text") != "vector_items":
    fail("message was not recovered")
if result.get("item_size") != 16:
    fail("float32 vlen=4 item_size must be 16")
if result.get("item_count") != 3:
    fail("expected three vector items")
print("CHECK_OK")
