from pathlib import Path

b=''.join(Path("capture.bits").read_text().split())
data=int(b[32:],2).to_bytes((len(b)-32)//8,'big')
def crc16(data):
    crc=0xffff
    for x in data:
        crc ^= x<<8
        for _ in range(8): crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc
if True:
    answer=data.decode()
else:
    answer=None
    for i in range(len(data)-5):
        if data[i:i+2]!=b'\xd3\x91': continue
        n=data[i+2]; body=data[i+2:i+3+n]; trailer=data[i+3+n:i+5+n]
        if len(trailer)==2 and crc16(body)==int.from_bytes(trailer,'big'):
            text=body[1:].decode(errors='ignore')
            if text.startswith('flag{'): answer=text
    if answer is None: raise RuntimeError("valid flag frame not found")
Path("answer.txt").write_text(answer)
