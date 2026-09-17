Find a Logic Bug
================

Goal
----
Usable means 10 <= sample <= 20. The loop is wrong — fix target.c so it prints usable=4.

Steps
-----
1) Press Start, then: ./run
2) In GDB, break near the if, run, display i and samples[i], step through
3) Fix the condition/loop in target.c
4) Prove: ./check — then Press Done
