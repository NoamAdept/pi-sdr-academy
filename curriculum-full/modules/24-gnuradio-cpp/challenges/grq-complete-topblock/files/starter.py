from complete_topblock import build_and_run
tb, sink = build_and_run()
print("edges:", len(tb.connections))
print("metrics:", sink.metrics)
