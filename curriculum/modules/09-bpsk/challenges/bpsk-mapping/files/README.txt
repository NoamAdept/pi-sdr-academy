# Discover BPSK Mapping

## Goal
Decode the capture to ASCII in `answer.txt`. Use `preamble.txt` (known first bytes) to resolve symbol→bit mapping.

Format note: IQ is little-endian interleaved float32. Average each group of 8 samples first. Pack bits MSB-first (`np.packbits`).

## Steps
1. Press Start → `./run`.
2. Decode / measure as asked; write `answer.txt`.
3. `./check` → press Done when it passes.
