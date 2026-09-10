# Unknown Capture

No sample-rate sidecar is supplied. `receiver_note.txt` gives one timing clue. Write `sample_rate_hz,carrier_hz,modulation` to `answer.txt`.

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).
Positive FFT frequency means counter-clockwise complex rotation.

Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
