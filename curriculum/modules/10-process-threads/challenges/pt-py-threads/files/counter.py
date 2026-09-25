"""Thread-safe parallel increments."""

from __future__ import annotations

import threading


def parallel_add(n_threads: int, per_thread: int) -> int:
    # TODO: spawn n_threads workers; each adds per_thread under a Lock.
    raise NotImplementedError("use threading + Lock")


if __name__ == "__main__":
    print(parallel_add(4, 1000))
