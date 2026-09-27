class FlowGraph:
    def __init__(self):
        self._e=[]
    def connect(self, src: str, dst: str) -> None:
        raise NotImplementedError
    def edges(self):
        raise NotImplementedError
