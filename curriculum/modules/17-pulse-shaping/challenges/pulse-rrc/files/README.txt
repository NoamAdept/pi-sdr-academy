# Estimate RRC Roll-Off

## Task
Compare `measured_rrc` against the candidate taps in `pulse_data.npz`. Write the matching roll-off as `0.20`, `0.35`, or `0.50`.

The supplied artifact is `pulse_data.npz`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

Load NPZ arrays with `np.load("pulse_data.npz")`; print `.files`, shapes, and
small slices. SciPy convolution/filtering and NumPy FFTs are sufficient.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
