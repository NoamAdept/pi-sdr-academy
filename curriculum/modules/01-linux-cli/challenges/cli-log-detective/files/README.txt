Log Detective
=============

Goal
----
Count WARN lines in receiver.log by component. Write report.txt.

Deliverable
-----------
  report.txt — one line per component, alphabetically:
    component=count
  Only level=WARN counts (example: audio=2).

Steps
-----
1) Press Start, open this folder.
2) Inspect receiver.log (grep / cut / sort / uniq help).
3) Write report.txt, then run:

     ./check

4) Press Done in the dojo when check passes.
