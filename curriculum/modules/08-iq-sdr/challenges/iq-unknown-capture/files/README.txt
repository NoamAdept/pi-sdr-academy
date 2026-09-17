# Unknown Capture

## Goal
No sample-rate sidecar. Use `receiver_note.txt`. Write `sample_rate_hz,carrier_hz,modulation` to `answer.txt`.

Format note: IQ files are little-endian interleaved float32 (I0,Q0,I1,Q1,...).
`sample_rate.txt` is samples/second when present.

## Steps
1. Press Start → `./run` (prints useful measurements).
2. Solve (edit code or write `answer.txt` as asked).
3. `./check` → press Done when it passes.
