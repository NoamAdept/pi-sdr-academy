# Decode Clean BPSK

## Goal
Decode the 8-samples/symbol capture and write the recovered ASCII flag to `answer.txt`.

Format note: IQ is little-endian interleaved float32. Average each group of 8 samples first. Pack bits MSB-first (`np.packbits`).

## Steps
1. Press Start → `./run`.
2. Decode / measure as asked; write `answer.txt`.
3. `./check` → press Done when it passes.
