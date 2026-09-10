#!/usr/bin/env python3

def parse_frames(data):
    # TODO
    return []

if __name__ == "__main__":
    import sys
    raw = bytes.fromhex(sys.argv[1])
    for payload in parse_frames(raw):
        print(payload.hex())
