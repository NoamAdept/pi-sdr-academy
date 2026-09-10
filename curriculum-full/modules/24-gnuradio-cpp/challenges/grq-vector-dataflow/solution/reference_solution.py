import numpy as np
from lib_flow import FloatToU8, VectorSink, VectorSource, run_chain

ENCODED = [118, 101, 99, 116, 111, 114, 95, 105, 116, 101, 109, 115]

def recover():
    source=VectorSource(ENCODED,np.float32,4); sink=VectorSink(np.uint8)
    out=run_chain(source,FloatToU8(),sink)
    return {"text":bytes(out).decode(),"item_size":source.item_size,"item_count":len(source.data)}
