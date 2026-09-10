# Recreate a Flowgraph in Python

Recreate: Multiply Const(0.25) → FIR low-pass(1200 Hz, 101 taps) → keep every second sample. Save `output.npy`.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).
GNU Radio Companion is optional; `optional.grc` sketches the same blocks.

Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
