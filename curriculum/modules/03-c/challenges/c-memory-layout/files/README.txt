Decode a Binary Header
======================

Goal
----
Implement decode_header in layout.c.

Layout
------
  tag[2] | sequence uint16 LE | flags byte | length byte
Return false for invalid input.

Steps
-----
1) Press Start and open layout.c.
2) Implement decode_header, then: ./check
3) Press Done when check passes.
