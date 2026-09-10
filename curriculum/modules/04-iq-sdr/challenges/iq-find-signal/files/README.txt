# Find a Signal in Spectrum

Find the strongest FFT frequency and write it in Hz to `answer.txt` (tolerance ±5 Hz).

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).
Positive FFT frequency means counter-clockwise complex rotation.

Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
