# Find the Header

## Task
Frames repeat in `capture.bits`. Find sync word D3 91, then interpret the next byte as payload length.

The supplied artifact is `capture.bits`. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.

The capture is an ASCII string of 0 and 1. Bits inside bytes are MSB first.
The protocol is fictional and the capture is entirely offline.

Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
