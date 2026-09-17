Decode Binary Records
=====================

Goal
----
Complete decode_records in decode.py.

Record layout (7 bytes each)
----------------------------
  uint32 LE frequency_hz
  int16  LE power_db
  uint8  status

Steps
-----
1) Press Start and open decode.py.
2) Try:  python3 decode.py samples.bin
3) Prove: ./check
4) Press Done when check passes.
