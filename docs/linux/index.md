# Linux command reference (offline)

Essential commands for Module 0–1. Prefer `man <cmd>` for full detail.

## Navigation & files

| Command | Purpose |
|---------|---------|
| `pwd` | Print working directory |
| `ls -la` | List all files (incl. hidden) |
| `cd path` | Change directory |
| `find . -type f -name '*flag*'` | Find files |
| `cat` / `less` | Read files |
| `tree` | Visualize directory tree |
| `file` | Guess file type |
| `stat` | Metadata + mode bits |
| `chmod` | Change permissions |
| `chown` / `chgrp` | Change owner (when permitted) |
| `cp` `mv` `rm` `mkdir` | File ops |
| `du -h` `df -h` | Disk usage |

## Text & pipelines

| Command | Purpose |
|---------|---------|
| `grep -RIn pattern` | Search |
| `sed` | Stream edit |
| `awk` | Column/field processing |
| `sort` `uniq` `cut` `tr` | Filters |
| `wc` | Counts |
| `head` `tail` | Slices |
| `\|` | Pipe stdout → stdin |

## Processes & /proc

| Command | Purpose |
|---------|---------|
| `ps aux` | Process list |
| `pgrep -af name` | Find by name |
| `top` / `htop` | Live view |
| `kill` / `kill -9` | Signals |
| `cat /proc/PID/cmdline` | Argv (NUL-separated) |
| `readlink /proc/PID/cwd` | Working directory |
| `tr '\\0' '\\n' < /proc/PID/environ` | Environment |

## Networking (local)

| Command | Purpose |
|---------|---------|
| `ss -lntp` | Listening sockets |
| `ip addr` / `ip route` | Interfaces/routes |
| `nc` | Netcat client/server |
| `curl http://127.0.0.1:...` | Local HTTP |

## See also

- `man bash`, `man proc`, `man chmod`
- [Bash docs](../bash/index.md)
- [Troubleshooting](../troubleshooting/index.md)
