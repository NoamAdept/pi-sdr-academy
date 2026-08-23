Find the Flag
=============

You are already in the challenge folder.

The real flag is hidden somewhere under labyrinth/. Explore with:

  pwd
  ls -la
  find . -type f
  cat FILE

README and hint files may help. When you find a value shaped like
flag{...}, either copy it to the academy flag file and submit:

  printf '%s\n' 'flag{...}' > "$(cat .flagpath 2>/dev/null || echo $HOME/flag.txt)"
  academy submit

Or submit it directly (keep the quotes in zsh):

  academy submit 'flag{...}'
