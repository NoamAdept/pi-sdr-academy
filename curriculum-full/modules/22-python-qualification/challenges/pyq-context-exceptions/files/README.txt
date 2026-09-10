GUARD A RECEIVER SESSION

Complete receiver_session.py.

ReceiverSession is a context manager:
- __enter__ marks it open and returns self
- __exit__ always marks it closed
- add() only works while open

parse_sample() accepts text such as "alpha,-67.5". It must raise the custom
SampleFormatError for a missing comma, empty station, or non-numeric dBm.

collect() must use `with`, and a complete try/except/else/finally:
- except: save bad input strings in session.errors
- else: add valid parsed samples
- finally: increment session.attempted

Exceptions from inside a with block must not be suppressed.
Run `python3 receiver_session.py`, then `./check`.
