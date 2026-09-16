Process Hunt
============

Goal
----
A process is a running program. Start the helper, learn a few facts about it,
and write them in report.txt.

Steps
-----
1) Start it:

     ./run

2) Find its process number:

     ps aux | grep helper

3) Learn its full start command and working folder (see notes in this folder).

4) In the start command, find --notes /some/path/note.txt — open that file,
   copy the secret_code.

5) Fill all 5 lines in report.txt, then run:

     ./check

6) Press Done in the dojo.
