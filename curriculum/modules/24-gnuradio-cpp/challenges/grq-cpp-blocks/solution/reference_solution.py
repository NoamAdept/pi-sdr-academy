from lib_flow import MultiplyConst, VectorSink, VectorSource, top_block
def build_and_run():
    source, gain, sink = VectorSource.make([1,2,3,4]), MultiplyConst.make(3), VectorSink.make()
    tb = top_block(); tb.connect(source, gain, sink); tb.run()
    return tb, sink
