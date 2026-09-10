from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Tag:
    offset: int
    key: str
    value: str

@dataclass
class Stream:
    items: np.ndarray
    tags: list

class TaggedSource:
    def __init__(self, items, tags):
        self.stream = Stream(np.asarray(items), list(tags))

class CopyBlock:
    def process(self, stream):
        return Stream(stream.items.copy(), list(stream.tags))

class TaggedSink:
    def __init__(self):
        self.items, self.tags, self.messages = None, [], []
    def consume(self, stream):
        self.items, self.tags = stream.items.copy(), list(stream.tags)
    def post_message(self, port, payload):
        self.messages.append((port, payload))

def run(source, blocks, sink):
    stream = source.stream
    for block in blocks:
        stream = block.process(stream)
    sink.consume(stream)
