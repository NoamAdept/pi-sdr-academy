Shell Automation
================

Goal
----
Finish inventory.sh so it builds a manifest of .iq files.

Deliverable
-----------
  Running: ./inventory.sh DIRECTORY
  Creates: manifest.txt in the current directory
  Lines:   filename,size,sha256  (only .iq files, sorted by name)

Steps
-----
1) Press Start and open inventory.sh.
2) Implement the script for the usage above.
3) Prove it:

     ./check

   Check uses a fresh temporary directory — your script must work generally.

4) Press Done when check passes.
