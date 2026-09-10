Process Hunt
============

What is this?
-------------
A "process" is a program that is currently running.
Every process has a process number.

Your job is to find a helper program after you start it, learn a few
facts about it, and write those facts in report.txt.

Steps
-----
1) Start it:
     ./run

2) Find its process number:
     ps aux | grep helper

3) Learn its full start command and its folder
   (see README / challenge text for Linux vs Mac commands).

4) In the start command, find:
     --notes /some/path/note.txt
   Open that file with cat. Copy the secret_code.

5) Fill report.txt (all 5 lines), then:
     ./check

6) If check succeeds, submit in the dojo UI (Go with an empty flag box, or paste the flag).

You cannot (and should not need to) read how ./run or ./check work inside.
