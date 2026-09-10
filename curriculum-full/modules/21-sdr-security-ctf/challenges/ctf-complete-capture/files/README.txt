# Complete Capture CTF

## Task
Find and decode a weak offset QPSK channel, correct timing/carrier, and parse its CRC-protected fictional packet. Parameters are bounded in README.

The supplied artifact is `capture.iq`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

IQ format is little-endian interleaved float32: I0,Q0,I1,Q1,...
Every radio frame ultimately contains either AA AA AA AA + length + plaintext,
or fictional LumaLink frames: D3 91 + length + payload + CRC-16/CCITT-FALSE.
Use plots only as diagnostics; a script should produce the final answer.

Search bounds: samples/symbol is one of 4, 6, or 8; carrier offset is within
+/-600 Hz; pulse shaping is rectangular or RRC with roll-off 0.20, 0.35, or
0.50. The modulation is BPSK or Gray QPSK. These bounds are deliberately wide
enough that measurements, not guessing, should select each parameter.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
