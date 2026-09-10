import numpy as np
from dsp_flow import deterministic_capture, freq_xlating_fir, lowpass_taps, spectral_peak

SAMPLE_RATE = 8000
THROTTLE_RATE = 8000
def analyze():
    samples = deterministic_capture(SAMPLE_RATE)
    # TODO: translate 2200 Hz to baseband with a 500 Hz, 129-tap low-pass.
    # TODO: magnitude, trim 256 edge samples, remove mean, and find envelope peak.
    return {"throttle_rate": THROTTLE_RATE, "magnitude_mean": 0.0, "envelope_peak_hz": 0.0}
