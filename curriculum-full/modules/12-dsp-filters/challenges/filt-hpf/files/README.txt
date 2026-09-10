# High-pass Filter

Create `output.npy` retaining 3000 Hz and attenuating 300 Hz by at least 20 dB. Use a high-pass filter.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).


Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
