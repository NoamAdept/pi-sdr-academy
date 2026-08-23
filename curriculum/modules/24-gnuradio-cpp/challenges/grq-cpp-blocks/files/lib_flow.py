from __future__ import annotations
from dataclasses import dataclass
import numpy as np

class Block:
    inputs = 1
    outputs = 1
    def process(self, value):
        return value

class VectorSource(Block):
    inputs = 0
    def __init__(self, values):
        self.values = np.asarray(values)
    @classmethod
    def make(cls, values):
        return cls(values)
    def process(self, value=None):
        return self.values.copy()

class VectorSink(Block):
    outputs = 0
    def __init__(self):
        self.data = None
    @classmethod
    def make(cls):
        return cls()
    def process(self, value):
        self.data = np.asarray(value).copy()
        return self.data

class MultiplyConst(Block):
    def __init__(self, gain):
        self.gain = gain
    @classmethod
    def make(cls, gain):
        return cls(gain)
    def process(self, value):
        return np.asarray(value) * self.gain

class Add(Block):
    inputs = 2
    def process(self, value):
        return np.asarray(value[0]) + np.asarray(value[1])

@dataclass(frozen=True)
class Endpoint:
    block: Block
    port: int = 0

class top_block:
    def __init__(self):
        self.connections = []
    def connect(self, *nodes):
        endpoints = [n if isinstance(n, Endpoint) else Endpoint(n) for n in nodes]
        self.connections.extend(zip(endpoints, endpoints[1:]))
    def _input(self, block, port, cache):
        edge = next((e for e in self.connections if e[1] == Endpoint(block, port)), None)
        if edge is None:
            raise RuntimeError(f"unconnected input {port} on {type(block).__name__}")
        return self._eval(edge[0].block, cache)
    def _eval(self, block, cache):
        if block in cache:
            return cache[block]
        if block.inputs == 0:
            value = block.process()
        elif block.inputs == 1:
            value = block.process(self._input(block, 0, cache))
        else:
            value = block.process([self._input(block, p, cache) for p in range(block.inputs)])
        cache[block] = value
        return value
    def run(self):
        cache = {}
        sinks = {edge[1].block for edge in self.connections if edge[1].block.outputs == 0}
        for sink in sinks:
            self._eval(sink, cache)
