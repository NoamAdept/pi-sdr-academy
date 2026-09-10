# Bits into Bytes

## Task
Convert the ASCII 0/1 stream in `capture.bits` into bytes, MSB first. Ignore the 32-bit alternating lead-in.

The supplied artifact is `capture.bits`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

The capture is an ASCII string of 0 and 1. Bits inside bytes are MSB first.
The protocol is fictional and the capture is entirely offline.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
