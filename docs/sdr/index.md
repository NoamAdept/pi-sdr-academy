# SDR / IQ fundamentals (offline)

Baseline curriculum uses **software IQ files** only. No dongle required.

## IQ files

Common educational format: interleaved `float32` little-endian pairs `(I0, Q0, I1, Q1, ...)`.

```python
import numpy as np
raw = np.fromfile("capture.iq", dtype=np.float32)
iq = raw[0::2] + 1j * raw[1::2]
```

Always document **sample rate** alongside the file (sidecar `.txt` / challenge YAML).

## What to measure first

1. Sample rate (from metadata)
2. Duration = `N / fs`
3. Spectrum peak location(s)
4. Approximate bandwidth
5. Time-domain amplitude / clipping

## Impairment vocabulary

| Impairment | Symptom |
|------------|---------|
| Frequency offset | Constellation spins; spectral peak off DC after supposed baseband |
| Phase offset | Static constellation rotation |
| Timing offset | Eye closure; decision jitter |
| Noise | Clouded constellation |
| ISI | Eye smearing from wrong pulse / mismatch |

## Optional hardware (never required)

RTL-SDR packages live in the offline bundle as **optional-hardware**. Complete the academy with file sources first.

## See also

- [Digital communications](../digital-comms/index.md)
- [GNU Radio](../gnuradio/index.md)
