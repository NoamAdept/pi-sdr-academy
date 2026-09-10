from dsp_flow import *
def build_and_run():
    rate=8000; source=Source(deterministic_capture(rate)); throttle=Throttle(rate)
    xlate=FrequencyXlatingFIR(lowpass_taps(500,rate,129),2200,rate)
    mag=ComplexToMag(); sink=MetricsSink(rate); tb=top_block()
    tb.connect(source,throttle,xlate,mag,sink); tb.run()
    return tb,sink
