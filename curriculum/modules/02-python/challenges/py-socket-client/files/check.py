#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import importlib.util, socket, threading
s=importlib.util.spec_from_file_location("student","client.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
server=socket.socket(); server.bind(("127.0.0.1",0)); server.listen(1); port=server.getsockname()[1]
seen=[]
def serve():
    c,_=server.accept()
    with c:
        data=b""
        while not data.endswith(b"\n"): data += c.recv(64)
        seen.append(data)
        c.sendall(b"channel=12 "); c.sendall(b"power=-51\n")
    server.close()
t=threading.Thread(target=serve, daemon=True); t.start()
got=m.request_reading("127.0.0.1",port,12); t.join(3)
if t.is_alive():
    server.close()
    fail("client did not finish the localhost exchange")
if seen != [b"READ 12\n"]: fail("send exactly READ, a space, the channel, and newline")
if got != "channel=12 power=-51": fail("receive and return the complete stripped reply")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
