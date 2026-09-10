from lib_flow import Add, Endpoint, MultiplyConst, VectorSink, VectorSource, top_block
def build_and_run():
    a,b=VectorSource.make([142,152,134,206,224,228]),VectorSource.make([62,64,60,0,22,10])
    add,gain,sink,tb=Add(),MultiplyConst.make(.5),VectorSink.make(),top_block()
    tb.connect(a,Endpoint(add,0)); tb.connect(b,Endpoint(add,1)); tb.connect(add,gain,sink); tb.run()
    return tb,sink
