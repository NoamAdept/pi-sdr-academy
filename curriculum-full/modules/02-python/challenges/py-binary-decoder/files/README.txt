Complete decode_records in decode.py.
Record layout (7 bytes):
  uint32 little-endian frequency_hz
  int16  little-endian power_db
  uint8  status
Run `python3 decode.py samples.bin`, then ./check.
