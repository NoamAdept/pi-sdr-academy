# DSP fundamentals (offline)

Software-first DSP on the Pi using NumPy/SciPy. GNU Radio appears in Module 13.

## Core ideas

1. **Sampling** — continuous → discrete at rate \(f_s\). Nyquist: representable bandwidth \(\le f_s/2\).
2. **Aliasing** — frequencies above Nyquist fold back; prevent with anti-alias filtering before decimation.
3. **Sinusoids** — \(x[n] = A\cos(2\pi f n / f_s + \phi)\).
4. **Complex baseband / IQ** — \(x = I + jQ\); spectrum need not be Hermitian-symmetric.
5. **FFT** — reveals frequency content; bin width \(\approx f_s / N\).
6. **Filtering** — FIR/IIR; convolution in time = multiply in frequency.
7. **Mixing** — multiply by \(e^{j2\pi f_0 n/f_s}\) to translate spectrum.
8. **Decimation / interpolation** — change sample rate with filtering.

## Minimal NumPy patterns

```python
import numpy as np

fs = 48_000
t = np.arange(0, 0.05, 1 / fs)
x = 0.5 * np.sin(2 * np.pi * 1000 * t)

# FFT magnitude
X = np.fft.rfft(x * np.hanning(len(x)))
freqs = np.fft.rfftfreq(len(x), 1 / fs)
peak = freqs[np.argmax(np.abs(X))]
```

## Pi performance notes

- Prefer `float32` IQ for large captures.
- Keep challenge captures short (tens of thousands to a few million samples).
- Prototype in Python; move hot loops to C++ later.

## See also

- [FFT](../dsp/index.md) (expand in-module)
- [SDR / IQ](../sdr/index.md)
- [Digital communications](../digital-comms/index.md)
