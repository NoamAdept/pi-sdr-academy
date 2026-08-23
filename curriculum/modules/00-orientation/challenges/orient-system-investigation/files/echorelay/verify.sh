#!/bin/sh
set -eu
# Contract: EchoRelay must answer PING on 127.0.0.1:9471
HOST=127.0.0.1
PORT=9471
if command -v nc >/dev/null 2>&1; then
  RESP=$(printf 'PING\n' | nc -w 2 "$HOST" "$PORT" || true)
else
  RESP=$(python3 - <<PY
import socket
s=socket.create_connection(("127.0.0.1", 9471), timeout=2)
s.sendall(b"PING\n")
print(s.recv(256).decode(), end="")
s.close()
PY
)
fi
echo "response: $RESP"
echo "$RESP" | grep -q 'flag{'
echo "VERIFY OK"
echo "$RESP" | tr -d '\r' | grep -o 'flag{[^}]*}' | head -1
