#!/usr/bin/env python3
import socket
import sys

def request_reading(host, port, channel):
    # TODO: connect, send one READ line, and receive the full reply
    return ""

if __name__ == "__main__":
    print(request_reading(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])))
