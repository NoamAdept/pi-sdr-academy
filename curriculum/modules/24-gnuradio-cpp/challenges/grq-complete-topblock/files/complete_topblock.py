from dsp_flow import (ComplexToMag, FrequencyXlatingFIR, MetricsSink, Source,
                      Throttle, deterministic_capture, lowpass_taps, top_block)

def build_and_run():
    rate = 8000
    source = Source(deterministic_capture(rate))
    # TODO: construct throttle, translating FIR (center 2200), magnitude, sink.
    # TODO: connect source -> throttle -> xlating FIR -> magnitude -> sink.
    # TODO: run and return (tb, sink).
    return top_block(), MetricsSink(rate)
