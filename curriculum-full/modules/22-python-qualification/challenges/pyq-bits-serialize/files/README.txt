DECODE THE BINARY RADIO RECORD

RAW_RECORD is a 26-byte record captured from a receiver. Its layout is:

  >2sBBI18s
  >      big-endian / network byte order
  2s     magic bytes, must be b"PQ"
  B      version, must be 1
  B      status: bit 0 active, bit 1 locked, bit 2 calibrated
  I      center frequency in Hz
  18s    flag field, each byte XOR encoded with key 0x5A

Complete:
- decode_status() using bitwise operators
- parse_record() using struct.unpack and the custom RecordError
- RadioRecord.to_json() using dataclasses + json
- pack_record() using struct.pack, the inverse of parsing

The provided record's recovered flag_field should read `pyq_bits_serialize`.
Your packing function must also work for other valid records.

Run `python3 radio_record.py`, then `./check`.
