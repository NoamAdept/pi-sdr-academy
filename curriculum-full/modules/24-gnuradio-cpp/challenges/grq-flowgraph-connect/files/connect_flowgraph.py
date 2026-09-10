from lib_flow import Add, Endpoint, MultiplyConst, VectorSink, VectorSource, top_block

def build_and_run():
    a = VectorSource.make([142, 152, 134, 206, 224, 228])
    b = VectorSource.make([62, 64, 60, 0, 22, 10])
    add, gain, sink, tb = Add(), MultiplyConst.make(0.5), VectorSink.make(), top_block()
    # TODO: connect a and b to add ports 0 and 1.
    # TODO: connect add -> gain -> sink and run.
    return tb, sink
