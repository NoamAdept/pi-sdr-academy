from build_flowgraph import build_and_run
tb, sink = build_and_run()
print("connections:", len(tb.connections))
print("sink:", None if sink.data is None else sink.data.tolist())
