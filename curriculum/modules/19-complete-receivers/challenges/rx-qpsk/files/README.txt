# Build a QPSK Receiver

## Task
Decode Gray QPSK at 8 sps. Symbols map bit pairs 00,01,11,10 counter-clockwise from +I.

The supplied artifact is `capture.iq`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

IQ format is little-endian interleaved float32: I0,Q0,I1,Q1,...
Every radio frame ultimately contains either AA AA AA AA + length + plaintext,
or fictional LumaLink frames: D3 91 + length + payload + CRC-16/CCITT-FALSE.
Use plots only as diagnostics; a script should produce the final answer.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
