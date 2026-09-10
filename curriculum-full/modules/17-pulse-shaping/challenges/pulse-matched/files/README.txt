# Choose the Matched Filter

## Task
Filter `received` with each candidate in `pulse_data.npz` and compare symbol-spaced eye opening. Write the best filter name: `boxcar`, `rrc`, or `differentiator`.

The supplied artifact is `pulse_data.npz`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

Load NPZ arrays with `np.load("pulse_data.npz")`; print `.files`, shapes, and
small slices. SciPy convolution/filtering and NumPy FFTs are sufficient.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
