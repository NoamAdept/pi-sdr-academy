# YOUR CODE HERE: import dbm_to_quality from the radio_tools package.

READINGS = [-35, -67, -92]


def build_report() -> list[str]:
    return [f"{value} dBm: {dbm_to_quality(value)}" for value in READINGS]


if __name__ == "__main__":
    print("\n".join(build_report()))
