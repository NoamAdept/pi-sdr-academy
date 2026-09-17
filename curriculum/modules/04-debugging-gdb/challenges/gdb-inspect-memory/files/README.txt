Inspect Memory
==============

Goal
----
At inspect_packet, examine 8 bytes from packet.

Deliverable
-----------
  answer.txt — lowercase hex bytes, no 0x, spaces between (e.g. 41 42 ...)

Steps
-----
1) Press Start, then: ./run
2) In GDB: break inspect_packet → run → x/8bx packet
3) Write answer.txt, then: ./check
4) Press Done when check passes.
