BUILD SIGNAL METER CLASSES

Complete signal_meter.py wherever you see YOUR CODE HERE.

SignalMeter must:
- remember its name and private sample list
- add numeric samples as floats
- return the arithmetic mean
- raise ValueError when no samples exist

CalibratedSignalMeter must:
- inherit SignalMeter behavior
- accept an offset from -20.0 through 20.0 dB
- reject offsets outside that range
- add the offset to the base average

Run `python3 signal_meter.py`, then `./check`.
