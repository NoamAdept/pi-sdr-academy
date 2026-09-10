Complete parse_frames(data) in protocol.py.
Frame: AA 55 | length | payload | XOR checksum
Return a list of payload bytes objects for valid frames.
The parser must recover and find valid frames after noise/bad frames.
Run ./check.
