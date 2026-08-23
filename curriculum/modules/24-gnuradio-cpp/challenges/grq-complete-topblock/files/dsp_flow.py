from __future__ import annotations
import numpy as np

def deterministic_capture(sample_rate=8000, count=4096):
    n = np.arange(count, dtype=np.float64)
    desired = (1.0 + 0.25*np.cos(2*np.pi*80*n/sample_rate)) * np.exp(
        2j*np.pi*2200*n/sample_rate
    )
    interferer = 0.35*np.exp(-2j*np.pi*900*n/sample_rate)
    return (desired + interferer).astype(np.complex64)

def lowpass_taps(cutoff, sample_rate, ntaps=129):
    n = np.arange(ntaps) - (ntaps - 1)/2
    taps = 2*cutoff/sample_rate * np.sinc(2*cutoff*n/sample_rate)
    taps *= np.hamming(ntaps)
    return taps / taps.sum()

def freq_xlating_fir(samples, taps, center_freq, sample_rate):
    n = np.arange(len(samples))
    shifted = samples * np.exp(-2j*np.pi*center_freq*n/sample_rate)
    return np.convolve(shifted, taps, mode="same")

def spectral_peak(samples, sample_rate, ignore_dc=False):
    x = np.asarray(samples)
    window = np.hanning(len(x))
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(x * window)))
    freq = np.fft.fftshift(np.fft.fftfreq(len(x), 1/sample_rate))
    if ignore_dc:
        spectrum[np.abs(freq) < 10] = 0
    return float(freq[np.argmax(spectrum)])

class Source:
    inputs = 0
    def __init__(self, values): self.values = np.asarray(values)
    def process(self, _=None): return self.values.copy()

class Throttle:
    def __init__(self, sample_rate): self.sample_rate = sample_rate
    def process(self, x): return np.asarray(x)

class FrequencyXlatingFIR:
    def __init__(self, taps, center, rate):
        self.taps, self.center, self.rate = taps, center, rate
    def process(self, x): return freq_xlating_fir(x, self.taps, self.center, self.rate)

class ComplexToMag:
    def process(self, x): return np.abs(x)

class MetricsSink:
    def __init__(self, rate): self.rate, self.metrics = rate, None
    def process(self, x):
        self.metrics = {
            "magnitude_mean": float(np.mean(x[256:-256])),
            "magnitude_peak_hz": abs(spectral_peak(x[256:-256]-np.mean(x[256:-256]), self.rate, True)),
        }
        return self.metrics

class top_block:
    def __init__(self): self.connections = []
    def connect(self, *blocks): self.connections.extend(zip(blocks, blocks[1:]))
    def run(self):
        starts = [a for a, _ in self.connections if not any(b is a for _, b in self.connections)]
        if len(starts) != 1: raise RuntimeError("graph needs exactly one source")
        current, value, seen = starts[0], None, set()
        while current is not None:
            if current in seen: raise RuntimeError("cycle in graph")
            seen.add(current)
            value = current.process(value)
            next_blocks = [b for a, b in self.connections if a is current]
            if len(next_blocks) > 1: raise RuntimeError("this simulator supports one linear chain")
            current = next_blocks[0] if next_blocks else None
        return value
