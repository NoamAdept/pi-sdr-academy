# Identify BPSK

## Goal
After averaging each 8-sample symbol, count the ideal constellation clusters. Write `two` to `answer.txt`.

Format note: IQ is little-endian interleaved float32. Average each group of 8 samples first. Pack bits MSB-first (`np.packbits`).

## Steps
1. Press Start → `./run`.
2. Decode / measure as asked; write `answer.txt`.
3. `./check` → press Done when it passes.
