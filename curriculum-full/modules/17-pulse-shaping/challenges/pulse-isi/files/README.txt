# Repair Inter-Symbol Interference

## Task
For each phase 0..7, sample `distorted` and measure the separation of the two BPSK clusters. Write the phase with the largest normalized eye opening.

The supplied artifact is `pulse_data.npz`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

Load NPZ arrays with `np.load("pulse_data.npz")`; print `.files`, shapes, and
small slices. SciPy convolution/filtering and NumPy FFTs are sufficient.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
