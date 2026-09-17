Text Extraction
===============

Goal
----
Pull every decimal MHz frequency out of bulletin.txt.

Deliverable
-----------
  frequencies.txt — unique numbers only (no "MHz"), one per line, numeric order.

Steps
-----
1) Press Start and read bulletin.txt.
2) Extract the numbers (grep -oE / sort -n / uniq help).
3) Write frequencies.txt, then:

     ./check

4) Press Done when check passes.
