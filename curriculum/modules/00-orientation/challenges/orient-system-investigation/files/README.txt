System Investigation
====================

Goal
----
EchoRelay is broken in more than one place. Repair it until verify prints
a flag. The flag exists only in the live PING reply — not in the scripts
on disk.

What you have
-------------
  echorelay/relayctl.sh              start / stop / status / logs
  echorelay/verify.sh                contract check (do not edit)
  echorelay/config/relay.conf        broken config (fix this)
  echorelay/config/relay.conf.example   known-good example
  echorelay/dropbox/                 token file the worker must read
  BRIEFING.md                        short incident note

Steps
-----
1) Press Start in the dojo.

2) Try the service and the contract:

     ./echorelay/relayctl.sh start
     ./echorelay/verify.sh

3) When something fails, read why:

     ./echorelay/relayctl.sh logs

4) Triage one fault at a time:
   - Is the worker still running? (`./echorelay/relayctl.sh status`)
   - Does config match the example? (listen port, dropbox path)
   - Can the worker read the token? (`ls -l echorelay/dropbox`)

5) After each fix, restart and re-check:

     ./echorelay/relayctl.sh stop
     ./echorelay/relayctl.sh start
     ./echorelay/verify.sh

6) When verify prints a flag{...}, paste it in the dojo — or press Done.

Do not edit verify.sh. No sudo. No internet.
