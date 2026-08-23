# Optional GNU Radio path

The graded path uses only Python and NumPy. If `python3 -c "import gnuradio"`
succeeds, recreate the same topology with `gr.top_block`, block `.make(...)`
factories, and `tb.connect((source, 0), (sink, 0))`.

Suggested mappings:
- simulator `VectorSource` / `VectorSink`: `blocks.vector_source_*` / `blocks.vector_sink_*`
- gain: `blocks.multiply_const_*`
- stream conversion: `blocks.float_to_char` (scale deliberately)
- translation/filtering: `filter.freq_xlating_fir_filter_ccc`
- magnitude: `blocks.complex_to_mag`
- rate limiting: `blocks.throttle` (only for graphs without hardware timing)

Call `start(); wait()` or `run()` on the top block. Stream tags use
`add_item_tag`; asynchronous messages use PMT ports and are not stream items.
