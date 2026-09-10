#!/usr/bin/env python3
import sys

def classify_signal(snr):
    # TODO: return weak, usable, or strong
    pass

def summarize(values):
    # TODO: return counts for all three labels
    pass

if __name__ == "__main__":
    values = [int(x) for x in sys.argv[1:]]
    print(summarize(values))
