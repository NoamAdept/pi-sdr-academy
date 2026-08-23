# Blocks, handles, and top blocks
Edit build_flowgraph.py. Factories such as VectorSource.make(...) model GNU
Radio C++ factories that return std::shared_ptr handles. Keep those handles,
connect source -> gain -> sink on one top_block, call run(), and return tb,sink.
