import numpy as np
from dsp_flow import deterministic_capture,freq_xlating_fir,lowpass_taps,spectral_peak
def analyze():
    rate=8000; x=deterministic_capture(rate); taps=lowpass_taps(500,rate,129)
    translated=freq_xlating_fir(x,taps,2200,rate); mag=np.abs(translated)[256:-256]
    return {"throttle_rate":rate,"magnitude_mean":float(np.mean(mag)),
            "envelope_peak_hz":abs(spectral_peak(mag-np.mean(mag),rate,True))}
