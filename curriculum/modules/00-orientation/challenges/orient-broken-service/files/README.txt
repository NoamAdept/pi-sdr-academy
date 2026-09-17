The Silent Port
===============

Goal
----
A tiny local web service ("beacon") will not start. Fix its config so it
listens on localhost, then prove it with a health check. The flag is only
in the live /health response — not in the files on disk.

What you have
-------------
  service/beaconctl.sh          start / stop / logs
  service/config/beacon.conf    broken config (fix this)
  service/config/beacon.conf.example   known-good example
  service/data/                 data files the service expects
  INCIDENT.txt                  short incident note

Steps
-----
1) Press Start in the dojo.

2) Try to bring the service up:

     ./service/beaconctl.sh start

3) If it fails, read why:

     ./service/beaconctl.sh logs

4) Compare the broken config to the example and fix only what is wrong:

     service/config/beacon.conf
     service/config/beacon.conf.example

   Typical issues: wrong listen address/port, wrong data file path.

5) Start again, then ask the live service for health (use the port from config):

     curl -s http://127.0.0.1:PORT/health

6) Paste the flag from that JSON into the dojo, or press Done.

You do not need root or the Internet. Keep the service on localhost.
