from pathlib import Path
import numpy as np
from scipy import signal

def crc16(data):
    crc=0xffff
    for b in data:
        crc ^= b<<8
        for _ in range(8): crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc

def rrc(beta,sps,span=8):
    t=np.arange(-span*sps//2,span*sps//2+1)/sps; h=np.empty_like(t,dtype=float)
    for i,x in enumerate(t):
        if abs(x)<1e-12: h[i]=1+beta*(4/np.pi-1)
        elif abs(abs(x)-1/(4*beta))<1e-10: h[i]=beta/np.sqrt(2)*((1+2/np.pi)*np.sin(np.pi/(4*beta))+(1-2/np.pi)*np.cos(np.pi/(4*beta)))
        else: h[i]=(np.sin(np.pi*x*(1-beta))+4*beta*x*np.cos(np.pi*x*(1+beta)))/(np.pi*x*(1-(4*beta*x)**2))
    return h/np.sqrt(np.sum(h*h))

a=np.fromfile("capture.iq",dtype="<f4").reshape(-1,2); x=a[:,0]+1j*a[:,1]
sps=8; fs=8000; protocol=False
n=np.arange(len(x)); x*=np.exp(-1j*(2*np.pi*(-78.125)*n/fs+np.deg2rad(51)))
taps = rrc(.35, sps)
# These values are the measured synchronization result; reproduce the measurements,
# do not simply copy them, when solving the challenge.
if True:
    y=signal.lfilter(taps,[1.0],x)
    first=4+len(taps)-1
else:
    y=signal.lfilter(taps,[1.0],x)
    first=4+sps-1
s=y[first::sps]
if 'qpsk'=="bpsk":
    bitstream=(s.real<0).astype(np.uint8)
else:
    # nearest Gray point, emitted as original bit pairs
    ang=np.angle(s); idx=np.argmin(abs(np.angle(np.exp(1j*(ang[:,None]-np.array([0,np.pi/2,np.pi,-np.pi/2]))))),axis=1)
    pairs=np.array([[0,0],[0,1],[1,1],[1,0]],np.uint8)
    bitstream=pairs[idx].ravel()

raw = np.packbits(bitstream).tobytes()
if protocol:
    answer = None
    for i in range(len(raw)-5):
        if raw[i:i+2] != b'\xd3\x91': continue
        n = raw[i+2]
        frame = raw[i+2:i+5+n]
        if len(frame) != n+3: continue
        body, got = frame[:-2], int.from_bytes(frame[-2:], 'big')
        if crc16(body) == got and body[1:].startswith(b'flag{'):
            answer = body[1:].decode()
            break
else:
    start = raw.find(b'\xaa\xaa\xaa\xaa')
    n = raw[start+4]
    answer = raw[start+5:start+5+n].decode()
if not answer: raise RuntimeError("frame not found")
Path("answer.txt").write_text(answer)

