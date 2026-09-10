from lib_flow import MultiplyConst, VectorSink, VectorSource, top_block

def build_and_run():
    source = VectorSource.make([1, 2, 3, 4])
    gain = MultiplyConst.make(3)
    sink = VectorSink.make()
    tb = top_block()
    # TODO: connect the same block handles in source -> gain -> sink order.
    # TODO: run the top block.
    return tb, sink
