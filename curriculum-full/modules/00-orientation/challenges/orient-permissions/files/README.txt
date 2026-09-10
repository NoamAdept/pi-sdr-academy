Permissions
===========

You are already in the challenge folder.

The flag is in vault/flag.txt, but you cannot read it yet.

1) Look at the files and their permissions:

     ls -l vault

2) Give yourself read permission on the flag file:

     chmod u+r vault/flag.txt

3) Read the flag:

     cat vault/flag.txt

4) Copy the flag to the academy flag file and submit:

     printf '%s\n' 'flag{...}' > "$(cat .flagpath 2>/dev/null || echo $HOME/flag.txt)"
     academy submit

You own the file. Do not use sudo, delete it, or change its owner.
