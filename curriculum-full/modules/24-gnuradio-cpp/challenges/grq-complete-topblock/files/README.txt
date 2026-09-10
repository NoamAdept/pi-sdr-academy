# Complete top block
Edit complete_topblock.py. Build exactly:
Source -> Throttle -> FrequencyXlatingFIR -> ComplexToMag -> MetricsSink.
Use rate 8000, lowpass_taps(500, rate, 129), and translation center 2200 Hz.
Run the graph and return the top block plus the same sink handle.
