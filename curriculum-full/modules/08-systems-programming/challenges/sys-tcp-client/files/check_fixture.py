#!/usr/bin/env python3
import socket, subprocess, sys, threading, time
def listener():
    s=socket.socket(); s.bind(("127.0.0.1",0)); s.listen(); return s
if sys.argv[1]=="run-client":
    s=listener(); port=s.getsockname()[1]
    p=subprocess.Popen([sys.executable,"client.py",str(port)],stdout=subprocess.PIPE,text=True)
    c,_=s.accept()
    with c:
        if c.recv(100).strip()==b"PING": c.sendall(b"PONG\n")
    print(p.communicate(timeout=3)[0],end=""); raise SystemExit(p.returncode)
else:
    probe=listener(); port=probe.getsockname()[1]; probe.close()
    p=subprocess.Popen([sys.executable,"server.py",str(port)])
    time.sleep(.2)
    def ask(msg,out):
        with socket.create_connection(("127.0.0.1",port),timeout=2) as c:
            c.sendall(msg); out.append(c.recv(100))
    out=[]; ts=[threading.Thread(target=ask,args=(x,out)) for x in (b"alpha",b"beta")]
    [t.start() for t in ts]; [t.join() for t in ts]; p.wait(timeout=3)
    print(out)
