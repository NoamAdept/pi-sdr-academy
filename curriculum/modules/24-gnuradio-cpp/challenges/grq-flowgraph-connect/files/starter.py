from connect_flowgraph import build_and_run
tb, sink = build_and_run()
print("edges:", len(tb.connections))
print("sink text:", None if sink.data is None else bytes(sink.data.astype("uint8")).decode(errors="replace"))
