Broken Service
==============

You are already in the challenge folder.

A small web service should run only on this computer, but its configuration
is broken.

1) Try to start it:

     ./service/beaconctl.sh start

2) If it fails, read the logs:

     ./service/beaconctl.sh logs

3) Compare these files and fix the broken values in beacon.conf:

     service/config/beacon.conf
     service/config/beacon.conf.example

4) Start it again, then fetch its health page using the port in the config:

     curl -s http://127.0.0.1:8765/health

5) Copy the flag from the response and submit it with quotes:

     academy submit 'flag{...}'

You do not need sudo or the Internet. Keep listen_host set to 127.0.0.1.
