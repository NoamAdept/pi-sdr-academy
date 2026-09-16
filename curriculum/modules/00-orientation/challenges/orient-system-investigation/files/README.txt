System Investigation
====================

Goal
----
EchoRelay has more than one problem. Fix it step by step until verify passes.

Steps
-----
1) Try to start and verify:

     ./echorelay/relayctl.sh start
     ./echorelay/verify.sh

2) Read the logs:

     ./echorelay/relayctl.sh logs

3) Compare config with the working example:

     echorelay/config/relay.conf
     echorelay/config/relay.conf.example

4) Check the token file permissions:

     ls -l echorelay/dropbox

5) After each fix:

     ./echorelay/relayctl.sh stop
     ./echorelay/relayctl.sh start
     ./echorelay/verify.sh

6) When verify prints a flag, paste it in the dojo — or press Done.

Do not edit verify.sh. No sudo. No internet.
