#!/usr/bin/env python3
import csv
import struct
import sys

def decode_records(path):
    # TODO
    return []

if __name__ == "__main__":
    rows = decode_records(sys.argv[1])
    with open("decoded.csv", "w", newline="") as f:
        out = csv.writer(f)
        out.writerow(["frequency_hz", "power_db", "status"])
        out.writerows(rows)
