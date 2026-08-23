System Investigation
====================

You are already in the challenge folder.

EchoRelay has more than one problem. Fix it one step at a time.

1) Try to start and verify it:

     ./echorelay/relayctl.sh start
     ./echorelay/verify.sh

2) Read the service logs:

     ./echorelay/relayctl.sh logs

3) Compare the current config with the working example:

     echorelay/config/relay.conf
     echorelay/config/relay.conf.example

4) Check whether the real token file exists and can be read:

     ls -l echorelay/dropbox

5) After each fix, stop and start the worker again:

     ./echorelay/relayctl.sh stop
     ./echorelay/relayctl.sh start
     ./echorelay/verify.sh

When verify prints a flag, submit it with quotes:

     academy submit 'flag{...}'

Do not edit verify.sh. You do not need sudo or the Internet.
