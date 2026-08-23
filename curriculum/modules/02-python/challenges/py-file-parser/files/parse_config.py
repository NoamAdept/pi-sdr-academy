#!/usr/bin/env python3
import sys

def parse_config(path):
    """Return a dict from name=value lines; ignore blanks and # comments."""
    # TODO
    return {}

if __name__ == "__main__":
    config = parse_config(sys.argv[1])
    with open("parsed.txt", "w") as out:
        for key in sorted(config):
            out.write(f"{key}={config[key]}\n")
