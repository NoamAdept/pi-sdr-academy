Environment
===========

Goal
----
The flag is split across two environment variables. Join them.

Steps
-----
1) Open the prepared lab shell:

     ./lab_shell.sh

2) List the lab variables:

     printenv | grep '^LAB_'

3) Join PART1 and PART2:

     printf '%s\n' "${LAB_FLAG_PART1}${LAB_FLAG_PART2}"

4) Copy the complete flag, type exit, then paste it in the dojo (or press Done).
