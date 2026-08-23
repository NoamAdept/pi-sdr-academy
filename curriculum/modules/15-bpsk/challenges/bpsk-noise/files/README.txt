# BPSK through Noise

Decode the 8-samples/symbol capture and write the recovered ASCII flag to `answer.txt`.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).
Average each group of 8 samples first. Packing is MSB-first (`np.packbits`).

Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
