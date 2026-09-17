Fix a Segfault
==============

Goal
----
The program crashes. Use GDB to find why, then fix target.c so it prints largest=12.

Steps
-----
1) Press Start, then: ./run  (see the crash)
2) GDB: run → bt → frame 0 → info locals
3) Fix target.c, rebuild via ./run, confirm largest=12
4) Prove: ./check — then Press Done
