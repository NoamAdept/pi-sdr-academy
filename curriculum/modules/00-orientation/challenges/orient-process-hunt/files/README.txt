Process Hunt
============

Goal
----
A helper process is running in the background. Gather five facts about it
into report.txt, then prove them with ./check.

Tools
-----
  ./run   ps   cat   /proc   ./check

Steps
-----
1) Press Start in the dojo, then launch the helper:

     ./run

2) Find its process id (PID):

     ps aux | grep helper

3) From /proc/<PID>/, learn the full start command and working directory
   (see notes in this folder if you need the exact paths).

4) In the start command, find --notes /some/path/note.txt — open that file
   and copy secret_code.

5) Fill every line in report.txt (use report.template as the shape), then:

     ./check

6) Press Done in the dojo when check passes.
