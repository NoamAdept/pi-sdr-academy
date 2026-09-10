Environment
===========

You are already in the challenge folder.

1) Open the prepared lab shell:

     ./lab_shell.sh

2) Inside it, list the environment variables:

     printenv | grep '^LAB_'

3) The flag is split into PART1 and PART2. Join them:

     printf '%s\n' "${LAB_FLAG_PART1}${LAB_FLAG_PART2}"

4) Copy the complete flag, then leave the lab shell:

     exit

5) Back in the challenge folder, write the flag and submit:

     printf '%s\n' 'flag{...}' > "$(cat .flagpath 2>/dev/null || echo $HOME/flag.txt)"
     academy submit

The value in decoy.env is not the answer.
