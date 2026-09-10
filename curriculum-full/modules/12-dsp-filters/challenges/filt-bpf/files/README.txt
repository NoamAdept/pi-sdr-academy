# Band-pass Filter

Create `output.npy` retaining 1800 Hz while attenuating 300 Hz and 3800 Hz by at least 20 dB.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).


Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
