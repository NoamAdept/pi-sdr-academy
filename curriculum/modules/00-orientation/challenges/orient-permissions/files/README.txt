Permissions
===========

Goal
----
The flag is in vault/flag.txt, but you cannot read it yet. Fix the mode bits.

Tools
-----
  ls -l   chmod   cat

Steps
-----
1) Press Start in the dojo.
2) Inspect modes:

     ls -l vault

3) Give your user read access:

     chmod u+r vault/flag.txt

4) Read and submit:

     cat vault/flag.txt

Paste the flag in the dojo, or press Done.

You own the file. Do not use sudo, delete it, or change its owner.
