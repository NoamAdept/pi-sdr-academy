Parse Framed Protocol Bytes
===========================

Goal
----
Complete parse_frames(data) in protocol.py.

Frame shape
-----------
  AA 55 | length | payload | XOR checksum
Return payload bytes for each valid frame. Skip noise and bad frames;
keep scanning so later good frames are still found.

Steps
-----
1) Press Start and open protocol.py.
2) Implement parse_frames, then: ./check
3) Press Done when check passes.
