# Build a DSP Pipeline

Select the +2400 Hz channel: mix it to 0 Hz, low-pass below 500 Hz, decimate by 4, and save 3000 complex samples as `output.npy`.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).


Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
