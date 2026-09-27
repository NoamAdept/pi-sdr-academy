Find the Flag
=============

You already know pwd, ls, and cat. Now explore a small maze of folders.

Goal
----
Find a secret shaped like flag{...} somewhere under labyrinth/.

Friendly steps
--------------
1. Press Start, then in the terminal:  cd challenge
2. Read this again:  cat README.txt
3. Look around:  ls -la
4. Enter the maze:  cd labyrinth    then    ls
5. Stuck? Try:  find . -type f
   That lists every file. Look for names with "flag" or "secret".
6. Print a file:  cat PATH/TO/FILE
7. Paste flag{...} in the dojo (or press Done).

Remember
--------
Hidden folders start with a dot (example: .cache).
ls -la shows them. find finds them too.
