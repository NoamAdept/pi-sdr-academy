from __future__ import annotations
import numpy as np

class VectorSource:
    def __init__(self, values, dtype=np.float32, vlen=1):
        self.dtype, self.vlen = np.dtype(dtype), int(vlen)
        data = np.asarray(values, dtype=self.dtype)
        if data.size % self.vlen:
            raise ValueError("data length must be divisible by vlen")
        self.data = data.reshape(-1, self.vlen)
    @property
    def item_size(self):
        return self.dtype.itemsize * self.vlen

class FloatToU8:
    input_dtype, output_dtype = np.dtype(np.float32), np.dtype(np.uint8)
    def process(self, items):
        flat = np.asarray(items, dtype=self.input_dtype).reshape(-1)
        return np.rint(flat).clip(0, 255).astype(self.output_dtype)

class VectorSink:
    def __init__(self, dtype=np.uint8):
        self.dtype, self.data = np.dtype(dtype), None
    def consume(self, items):
        self.data = np.asarray(items, dtype=self.dtype).copy()

def run_chain(source, converter, sink):
    converted = converter.process(source.data)
    sink.consume(converted)
    return sink.data
