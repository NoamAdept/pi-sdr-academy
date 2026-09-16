Broken Service
==============

Goal
----
A small local web service will not start. Fix its config, then read /health.

Steps
-----
1) Try to start it:

     ./service/beaconctl.sh start

2) If it fails, read the logs:

     ./service/beaconctl.sh logs

3) Compare and fix broken values in:

     service/config/beacon.conf
     service/config/beacon.conf.example

4) Start again, then:

     curl -s http://127.0.0.1:PORT/health

   (use the port from the config)

5) Press Done in the dojo when the health check works.
