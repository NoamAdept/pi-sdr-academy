# Remove Narrowband Interference

Create `output.npy` with a narrow notch at 1500 Hz. Reduce it by 25 dB while keeping 700 and 2300 Hz within 3 dB.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).


Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
