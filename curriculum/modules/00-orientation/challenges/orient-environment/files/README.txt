Environment
===========

Goal
----
The flag is split across two environment variables inside a lab shell. Join them.

Tools
-----
  ./lab_shell.sh   printenv   printf

Steps
-----
1) Press Start in the dojo.

2) Enter the prepared lab shell:

     ./lab_shell.sh

3) List lab variables:

     printenv | grep '^LAB_'

4) Join PART1 and PART2:

     printf '%s\n' "${LAB_FLAG_PART1}${LAB_FLAG_PART2}"

5) Copy the complete flag, type exit, then paste it in the dojo (or press Done).

Tip: reading lab_shell.sh will not show the live flag — use the environment.
