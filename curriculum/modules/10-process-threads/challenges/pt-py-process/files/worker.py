"""Return stdout from a real child process that prints msg."""

from __future__ import annotations

import subprocess
import sys


def run_echo(msg: str) -> str:
    # TODO: start a child with subprocess (sys.executable -c …)
    # and return its stripped stdout. Do not just `return msg`.
    raise NotImplementedError("spawn a child process")


if __name__ == "__main__":
    print(run_echo("process_ok"))
