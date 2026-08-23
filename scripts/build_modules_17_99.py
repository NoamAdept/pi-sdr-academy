#!/usr/bin/env python3
"""Build the small, deterministic datasets for Academy modules 17--21 and 99."""
from __future__ import annotations

import json
import os
import shutil
import textwrap
from pathlib import Path

import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "curriculum" / "modules"
RNG = np.random.default_rng(20260812)

SPECS = {
    "17-pulse-shaping": [
        ("pulse-observe", "Observe Symbol Pulses", "easy", "20-40 minutes", "flag{samples_reveal_symbol_pulses}", "pulse", "8",
         "Measure the spacing, in samples, between the impulses in `pulse_data.npz`. Write the integer to `answer.txt`."),
        ("pulse-compare", "Compare Pulse Shapes", "easy", "30-50 minutes", "flag{rrc_trades_bandwidth_for_ringing}", "pulse", "rrc",
         "Plot or inspect the spectra in `pulse_data.npz`. Write `rrc` for the waveform with the narrower occupied bandwidth, or `rect` for the other."),
        ("pulse-rc", "Raised-Cosine Nyquist Zeros", "medium", "45-75 minutes", "flag{raised_cosine_has_nyquist_zeros}", "pulse", "raised-cosine",
         "Inspect `pulse_data.npz`. Identify the pulse whose samples at nonzero symbol intervals are approximately zero. Write `raised-cosine`."),
        ("pulse-rrc", "Estimate RRC Roll-Off", "medium", "50-90 minutes", "flag{rolloff_controls_excess_bandwidth}", "pulse", "0.35",
         "Compare `measured_rrc` against the candidate taps in `pulse_data.npz`. Write the matching roll-off as `0.20`, `0.35`, or `0.50`."),
        ("pulse-matched", "Choose the Matched Filter", "medium", "60-100 minutes", "flag{matched_filters_maximize_sample_snr}", "pulse", "rrc",
         "Filter `received` with each candidate in `pulse_data.npz` and compare symbol-spaced eye opening. Write the best filter name: `boxcar`, `rrc`, or `differentiator`."),
        ("pulse-isi", "Repair Inter-Symbol Interference", "hard", "90-150 minutes", "flag{eye_opening_guides_timing_and_equalization}", "pulse", "2",
         "For each phase 0..7, sample `distorted` and measure the separation of the two BPSK clusters. Write the phase with the largest normalized eye opening."),
    ],
    "18-synchronization": [
        ("sync-static-phase", "Measure Static Phase", "easy", "30-50 minutes", "flag{phase_rotation_is_complex_multiplication}", "radio", None,
         "Decode the BPSK capture. It uses 8 samples/symbol, no frequency offset, and a constant phase of +35 degrees."),
        ("sync-identify-freq", "Identify Frequency Offset", "easy", "35-60 minutes", "flag{phase_slope_reveals_frequency_offset}", "radio", None,
         "Decode the BPSK capture. Sample rate is 8000 Hz, 8 samples/symbol, carrier offset is +125 Hz, and phase is +20 degrees."),
        ("sync-correct-phase", "Correct Unknown Phase", "medium", "50-90 minutes", "flag{known_preamble_resolves_phase_ambiguity}", "radio", None,
         "Decode BPSK with 8 samples/symbol and no CFO. Estimate constant phase from the 32-bit alternating preamble."),
        ("sync-correct-freq", "Correct Frequency Offset", "medium", "60-100 minutes", "flag{derotate_frequency_before_slicing_symbols}", "radio", None,
         "Decode BPSK at 8000 samples/s and 8 samples/symbol. Estimate the CFO (between -200 and +200 Hz) from preamble phase slope."),
        ("sync-timing", "Recover Symbol Timing", "medium", "70-110 minutes", "flag{timing_recovery_samples_the_open_eye}", "radio", None,
         "Decode BPSK at 8 samples/symbol. CFO is zero and phase is +15 degrees; the first symbol starts at an unknown sample phase 0..7."),
        ("sync-carrier-timing", "Joint Carrier and Timing Recovery", "hard", "100-180 minutes", "flag{carrier_and_timing_loops_complete_the_link}", "radio", None,
         "Recover a BPSK frame with unknown timing phase, phase, and CFO in ±200 Hz. Sample rate is 8000 Hz and nominal sps is 8."),
    ],
    "19-complete-receivers": [
        ("rx-bpsk", "Build a BPSK Receiver", "easy", "45-75 minutes", "flag{a_receiver_is_a_chain_of_verified_stages}", "radio", None,
         "Build a complete rectangular-pulse BPSK receiver. Parameters: 8000 Hz, 8 sps, zero offsets."),
        ("rx-qpsk", "Build a QPSK Receiver", "medium", "60-100 minutes", "flag{qpsk_carries_two_bits_per_symbol}", "radio", None,
         "Decode Gray QPSK at 8 sps. Symbols map bit pairs 00,01,11,10 counter-clockwise from +I."),
        ("rx-noisy-qpsk", "Receive Noisy QPSK", "medium", "75-120 minutes", "flag{averaging_and_preambles_defeat_noise}", "radio", None,
         "Decode noisy Gray QPSK at 8 sps. Average each symbol and use the known alternating preamble."),
        ("rx-offset-qpsk", "Receive Offset QPSK", "hard", "90-150 minutes", "flag{frequency_and_phase_correction_restore_qpsk}", "radio", None,
         "Decode Gray QPSK with +62.5 Hz CFO and +28 degrees phase at 8000 Hz, 8 sps."),
        ("rx-full", "Assemble the Full Receiver", "hard", "120-210 minutes", "flag{matched_sync_slice_frame_check}", "radio", None,
         "Decode an RRC-shaped QPSK frame. Given: 8000 Hz, 8 sps, roll-off 0.35. Timing, CFO, and phase require correction."),
        ("rx-unknown-params", "Receiver with Unknown Parameters", "hard", "150-240 minutes", "flag{measure_first_then_configure_the_receiver}", "radio", None,
         "Identify and decode an RRC-shaped capture. Sample rate is 12000 Hz; modulation is BPSK or QPSK, sps is one of 4, 6, 8, and CFO is within ±250 Hz."),
    ],
    "20-protocol-re": [
        ("proto-bit-byte", "Bits into Bytes", "easy", "30-50 minutes", "flag{msb_first_bits_form_bytes}", "protocol", None,
         "Convert the ASCII 0/1 stream in `capture.bits` into bytes, MSB first. Ignore the 32-bit alternating lead-in."),
        ("proto-header", "Find the Header", "easy", "40-65 minutes", "flag{repeated_frames_reveal_stable_headers}", "protocol", None,
         "Frames repeat in `capture.bits`. Find sync word D3 91, then interpret the next byte as payload length."),
        ("proto-packet", "Map a Packet", "medium", "55-90 minutes", "flag{length_fields_turn_streams_into_packets}", "protocol", None,
         "Parse fictional LumaLink frames: sync D3 91, one-byte length, payload, then two check bytes."),
        ("proto-crc", "Identify and Verify CRC", "medium", "75-120 minutes", "flag{crc16_catches_corrupted_frames}", "protocol", None,
         "Parse LumaLink, then retain only frames whose CRC-16/CCITT-FALSE over length+payload matches the big-endian trailer."),
        ("proto-unknown", "Reverse an Unknown Protocol", "hard", "100-180 minutes", "flag{patterns_make_unknown_protocols_legible}", "protocol", None,
         "Reverse the repeated fictional packet stream. Hints: a two-byte sync repeats; a nearby byte predicts frame size; two trailing bytes change avalanche-style."),
        ("proto-decoder", "Write a Reusable Decoder", "hard", "120-210 minutes", "flag{streaming_decoders_resynchronize_after_damage}", "protocol", None,
         "Decode `capture.bits`, which includes junk bits and one corrupt frame. Recover the valid payload beginning with `flag{` using sync, length, and CRC."),
    ],
    "21-sdr-security-ctf": [
        ("ctf-hidden-tx", "Find the Hidden Transmission", "medium", "60-100 minutes", "flag{spectral_search_finds_the_hidden_channel}", "radio", None,
         "A weak BPSK transmission is offset +500 Hz in a wider 16000 Hz capture. Mix it to baseband, then decode at 8 sps."),
        ("ctf-identify-mod", "Identify the Modulation", "medium", "70-110 minutes", "flag{constellation_moments_identify_qpsk}", "radio", None,
         "Determine whether the 8-sps capture is BPSK or Gray QPSK, then decode it. Carrier and timing are already aligned."),
        ("ctf-recover-bits", "Recover the Bitstream", "medium", "80-130 minutes", "flag{symbols_become_bits_then_bytes}", "radio", None,
         "Recover bits from 8-sps Gray QPSK and parse the embedded LumaLink frame (sync D3 91, length, payload, CRC)."),
        ("ctf-correct-impair", "Correct Capture Impairments", "hard", "100-170 minutes", "flag{impairments_fall_to_measure_correct_verify}", "radio", None,
         "Correct timing, CFO within ±200 Hz, and phase in an 8000 Hz RRC QPSK capture (8 sps, beta 0.35), then decode LumaLink."),
        ("ctf-re-protocol", "Reverse the Air Protocol", "hard", "120-210 minutes", "flag{radio_and_protocol_layers_fail_independently}", "radio", None,
         "Demodulate the RRC BPSK capture, infer the fictional framing from repeats, reject the bad CRC, and recover the valid flag payload."),
        ("ctf-complete-capture", "Complete Capture CTF", "hard", "150-270 minutes", "flag{complete_capture_analysis_connects_every_layer}", "radio", None,
         "Find and decode a weak offset QPSK channel, correct timing/carrier, and parse its CRC-protected fictional packet. Parameters are bounded in README."),
    ],
    "99-capstone-blackout": [
        ("capstone-blackout", "Final Capstone — Blackout", "hard", "3-6 hours", "flag{blackout_receiver_restores_the_last_message}", "radio", None,
         "Recover the final message from an unknown IQ capture: locate the channel, identify QPSK, synchronize, matched-filter, frame, and verify CRC."),
    ],
}

RADIO_CFG = {
    "sync-static-phase": ("bpsk", 8, 8000, 0, 35, 0, .03, False),
    "sync-identify-freq": ("bpsk", 8, 8000, 125, 20, 0, .03, False),
    "sync-correct-phase": ("bpsk", 8, 8000, 0, 67, 0, .04, False),
    "sync-correct-freq": ("bpsk", 8, 8000, -93.75, 40, 0, .04, False),
    "sync-timing": ("bpsk", 8, 8000, 0, 15, 5, .04, False),
    "sync-carrier-timing": ("bpsk", 8, 8000, 156.25, 73, 3, .06, False),
    "rx-bpsk": ("bpsk", 8, 8000, 0, 0, 0, .03, False),
    "rx-qpsk": ("qpsk", 8, 8000, 0, 0, 0, .03, False),
    "rx-noisy-qpsk": ("qpsk", 8, 8000, 0, 0, 0, .20, False),
    "rx-offset-qpsk": ("qpsk", 8, 8000, 62.5, 28, 0, .07, False),
    "rx-full": ("qpsk", 8, 8000, -78.125, 51, 4, .025, True),
    "rx-unknown-params": ("qpsk", 6, 12000, 187.5, 82, 2, .025, True),
    "ctf-hidden-tx": ("bpsk", 8, 16000, 500, 23, 0, .20, False),
    "ctf-identify-mod": ("qpsk", 8, 8000, 0, 0, 0, .05, False),
    "ctf-recover-bits": ("qpsk", 8, 8000, 0, 0, 0, .06, False),
    "ctf-correct-impair": ("qpsk", 8, 8000, -109.375, 64, 5, .025, True),
    "ctf-re-protocol": ("bpsk", 8, 8000, 46.875, 31, 3, .025, True),
    "ctf-complete-capture": ("qpsk", 8, 16000, 375, 77, 6, .025, True),
    "capstone-blackout": ("qpsk", 8, 16000, -437.5, 119, 5, .025, True),
}


def bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def packet(payload: bytes, corrupt=False) -> bytes:
    body = bytes([len(payload)]) + payload
    c = crc16(body) ^ (1 if corrupt else 0)
    return b"\xd3\x91" + body + c.to_bytes(2, "big")


def rrc(beta: float, sps: int, span=8) -> np.ndarray:
    t = np.arange(-span * sps // 2, span * sps // 2 + 1) / sps
    h = np.empty_like(t, dtype=float)
    for i, x in enumerate(t):
        if abs(x) < 1e-12:
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif beta and abs(abs(x) - 1 / (4 * beta)) < 1e-10:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * x * (1 - beta)) + 4 * beta * x * np.cos(np.pi * x * (1 + beta))) / (np.pi * x * (1 - (4 * beta * x) ** 2))
    return h / np.sqrt(np.sum(h * h))


def framed_payload(flag: str, protocol: bool, repeated=False) -> np.ndarray:
    payload = flag.encode()
    if protocol:
        raw = packet(b"STATUS:nominal") + packet(b"decoy", corrupt=True) + packet(payload)
    else:
        raw = b"\xaa\xaa\xaa\xaa" + bytes([len(payload)]) + payload
    if repeated:
        raw = raw + packet(b"STATUS:retry") + packet(payload)
    return bits(raw)


def modulate(flag: str, cfg, protocol=False, repeated=False):
    mod, sps, fs, cfo, phase, timing, noise, shaped = cfg
    b = framed_payload(flag, protocol, repeated)
    if mod == "bpsk":
        syms = 1 - 2 * b.astype(float)
    else:
        if len(b) % 2:
            b = np.r_[b, 0]
        pairs = b.reshape(-1, 2)
        # Gray: 00=+I, 01=+Q, 11=-I, 10=-Q.
        table = {(0, 0): 1, (0, 1): 1j, (1, 1): -1, (1, 0): -1j}
        syms = np.array([table[tuple(p)] for p in pairs]) / np.sqrt(1)
    up = np.zeros(len(syms) * sps, complex)
    up[::sps] = syms
    taps = rrc(.35, sps) if shaped else np.ones(sps)
    if shaped:
        # Flush the transmit filter so the final payload symbols are present.
        up = np.r_[up, np.zeros(len(taps) - 1, complex)]
    x = signal.lfilter(taps, [1.0], up)
    x = np.r_[np.zeros(timing, complex), x]
    n = np.arange(len(x))
    x *= np.exp(1j * (2 * np.pi * cfo * n / fs + np.deg2rad(phase)))
    x += noise * (RNG.normal(size=len(x)) + 1j * RNG.normal(size=len(x)))
    return x.astype(np.complex64), len(b), taps


def write_iq(path: Path, x: np.ndarray):
    np.column_stack((x.real, x.imag)).astype("<f4").tofile(path)


def pulse_dataset(cid: str, out: Path):
    sps = 8
    impulses = np.zeros(80)
    impulses[::sps] = np.tile([1, -1], 5)
    rect = np.ones(sps) / np.sqrt(sps)
    taps = {b: rrc(b, sps) for b in (.2, .35, .5)}
    if cid == "pulse-observe":
        np.savez(out, impulses=impulses, sample_rate_hz=8000, symbol_rate_baud=1000)
    elif cid == "pulse-compare":
        np.savez(out, rect=signal.convolve(impulses, rect), rrc=signal.convolve(impulses, taps[.35]), sps=sps)
    elif cid == "pulse-rc":
        rc = signal.convolve(taps[.35], taps[.35])
        np.savez(out, pulse_a=rect, pulse_b=rc / np.max(rc), sps=sps, center=np.argmax(rc))
    elif cid == "pulse-rrc":
        measured = taps[.35] + RNG.normal(0, .002, len(taps[.35]))
        np.savez(out, measured_rrc=measured, candidate_020=taps[.2], candidate_035=taps[.35], candidate_050=taps[.5], sps=sps)
    elif cid == "pulse-matched":
        tx = signal.convolve(impulses, taps[.35])
        received = tx + RNG.normal(0, .12, len(tx))
        np.savez(out, received=received, boxcar=rect, rrc=taps[.35], differentiator=np.array([1., -1.]), sps=sps)
    else:
        symbols = 1 - 2 * RNG.integers(0, 2, 200)
        up = np.zeros(len(symbols) * sps)
        up[::sps] = symbols
        root = rrc(.35, sps)
        shaped = signal.convolve(up, signal.convolve(root, root))
        distorted = np.r_[np.zeros(2), shaped] + RNG.normal(0, .06, len(shaped) + 2)
        np.savez(out, distorted=distorted, sps=sps)


def protocol_capture(cid: str, flag: str, out: Path):
    if cid == "proto-bit-byte":
        rawbits = np.r_[np.tile([1, 0], 16), bits(flag.encode())]
    elif cid == "proto-header":
        rawbits = bits(packet(b"TELEM:21") + packet(flag.encode()))
    elif cid == "proto-packet":
        rawbits = bits(packet(b"NODE:7") + packet(flag.encode()))
    elif cid == "proto-crc":
        rawbits = bits(packet(b"flag{wrong_frame}", True) + packet(flag.encode()))
    elif cid == "proto-unknown":
        rawbits = bits(packet(b"TEMP:19.5") + packet(b"VOLT:4.98") + packet(flag.encode()))
    else:
        rawbits = np.r_[RNG.integers(0, 2, 13), bits(packet(b"noise", True) + packet(flag.encode()) + packet(b"done"))]
    out.write_text("".join(map(str, rawbits.astype(int))) + "\n")


def checker(flag: str, expected: str | None) -> str:
    target = expected or flag
    return f"""from pathlib import Path
import os

FLAG = {flag!r}
EXPECTED = {target!r}

def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

try:
    answer = Path("answer.txt").read_text().strip()
except OSError:
    fail("create answer.txt first")
if answer.lower() != EXPECTED.lower():
    fail("answer.txt does not contain the recovered answer")
marker = Path(".flagpath")
out = Path(marker.read_text().strip()) if marker.is_file() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
try:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(FLAG + "\\n")
    print("Correct! Flag written to:", out)
except OSError:
    print(FLAG)
"""


def radio_solution(cid: str, flag: str, cfg, protocol: bool) -> str:
    mod, sps, fs, cfo, phase, timing, noise, shaped = cfg
    taps_line = "taps = rrc(.35, sps)" if shaped else "taps = np.ones(sps)"
    parse = """
raw = np.packbits(bitstream).tobytes()
if protocol:
    answer = None
    for i in range(len(raw)-5):
        if raw[i:i+2] != b'\\xd3\\x91': continue
        n = raw[i+2]
        frame = raw[i+2:i+5+n]
        if len(frame) != n+3: continue
        body, got = frame[:-2], int.from_bytes(frame[-2:], 'big')
        if crc16(body) == got and body[1:].startswith(b'flag{'):
            answer = body[1:].decode()
            break
else:
    start = raw.find(b'\\xaa\\xaa\\xaa\\xaa')
    n = raw[start+4]
    answer = raw[start+5:start+5+n].decode()
if not answer: raise RuntimeError("frame not found")
Path("answer.txt").write_text(answer)
"""
    return f"""from pathlib import Path
import numpy as np
from scipy import signal

def crc16(data):
    crc=0xffff
    for b in data:
        crc ^= b<<8
        for _ in range(8): crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc

def rrc(beta,sps,span=8):
    t=np.arange(-span*sps//2,span*sps//2+1)/sps; h=np.empty_like(t,dtype=float)
    for i,x in enumerate(t):
        if abs(x)<1e-12: h[i]=1+beta*(4/np.pi-1)
        elif abs(abs(x)-1/(4*beta))<1e-10: h[i]=beta/np.sqrt(2)*((1+2/np.pi)*np.sin(np.pi/(4*beta))+(1-2/np.pi)*np.cos(np.pi/(4*beta)))
        else: h[i]=(np.sin(np.pi*x*(1-beta))+4*beta*x*np.cos(np.pi*x*(1+beta)))/(np.pi*x*(1-(4*beta*x)**2))
    return h/np.sqrt(np.sum(h*h))

a=np.fromfile("capture.iq",dtype="<f4").reshape(-1,2); x=a[:,0]+1j*a[:,1]
sps={sps}; fs={fs}; protocol={protocol!r}
n=np.arange(len(x)); x*=np.exp(-1j*(2*np.pi*({cfo})*n/fs+np.deg2rad({phase})))
{taps_line}
# These values are the measured synchronization result; reproduce the measurements,
# do not simply copy them, when solving the challenge.
if {shaped!r}:
    y=signal.lfilter(taps,[1.0],x)
    first={timing}+len(taps)-1
else:
    y=signal.lfilter(taps,[1.0],x)
    first={timing}+sps-1
s=y[first::sps]
if {mod!r}=="bpsk":
    bitstream=(s.real<0).astype(np.uint8)
else:
    # nearest Gray point, emitted as original bit pairs
    ang=np.angle(s); idx=np.argmin(abs(np.angle(np.exp(1j*(ang[:,None]-np.array([0,np.pi/2,np.pi,-np.pi/2]))))),axis=1)
    pairs=np.array([[0,0],[0,1],[1,1],[1,0]],np.uint8)
    bitstream=pairs[idx].ravel()
{textwrap.dedent(parse)}
"""


def protocol_solution(cid: str) -> str:
    offset = 32 if cid == "proto-bit-byte" else (13 if cid == "proto-decoder" else 0)
    simple = cid == "proto-bit-byte"
    return f"""from pathlib import Path

b=''.join(Path("capture.bits").read_text().split())
data=int(b[{offset}:],2).to_bytes((len(b)-{offset})//8,'big')
def crc16(data):
    crc=0xffff
    for x in data:
        crc ^= x<<8
        for _ in range(8): crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc
if {simple!r}:
    answer=data.decode()
else:
    answer=None
    for i in range(len(data)-5):
        if data[i:i+2]!=b'\\xd3\\x91': continue
        n=data[i+2]; body=data[i+2:i+3+n]; trailer=data[i+3+n:i+5+n]
        if len(trailer)==2 and crc16(body)==int.from_bytes(trailer,'big'):
            text=body[1:].decode(errors='ignore')
            if text.startswith('flag{{'): answer=text
    if answer is None: raise RuntimeError("valid flag frame not found")
Path("answer.txt").write_text(answer)
"""


def challenge_yaml(module_dir: str, spec, file_names):
    cid, title, difficulty, eta, flag, kind, expected, task = spec
    module = module_dir.split("-", 1)[1]
    prereq = {"17-pulse-shaping": "qpsk", "18-synchronization": "pulse-shaping", "19-complete-receivers": "synchronization",
              "20-protocol-re": "complete-receivers", "21-sdr-security-ctf": "protocol-re", "99-capstone-blackout": "sdr-security-ctf"}[module_dir]
    files_yaml = "\n".join(f"  - {x}" for x in file_names)
    if cid == "capstone-blackout":
        hints = """  - level: 1
    text: "Start with a wide FFT: the signal is not centered. Estimate and remove the channel offset before deciding anything else."
  - level: 2
    text: "Try sps values 4, 6, and 8 and compare constellation compactness after RRC matched filters with roll-off 0.20, 0.35, and 0.50."
  - level: 3
    text: "The modulation is Gray QPSK. Use the repeated packet structure to resolve quadrant ambiguity and search timing phases."
  - level: 4
    text: "Look for D3 91, then length, payload, and big-endian CRC-16/CCITT-FALSE. Reject damaged frames before trusting plaintext."
"""
    else:
        hints = """  - level: 1
    text: "Run ./run and inspect array lengths, spectra, or repeated byte patterns before decoding."
  - level: 2
    text: "Turn the mission into measured stages; print one intermediate result after every transformation."
  - level: 3
    text: "IQ is little-endian interleaved float32. Bits are packed MSB first. Known or repeated preambles resolve ambiguity."
  - level: 4
    text: "The reference solution documents a compact path, but try to reproduce each inferred parameter yourself."
"""
    return f"""id: {cid}
module: {module}
title: "{title}"
difficulty: {difficulty}
estimated_time: "{eta}"
prerequisites:
  - module:{prereq}
objectives:
  - inspect_offline_signal_data
  - implement_and_verify_a_small_receiver_stage
  - recover_a_validated_result
mastery_evidence:
  - understand
  - implement
  - apply
description: |
  ## Mission
  {task}

  Work entirely offline in the supplied workspace. Run `./run`, read
  `README.txt`, create `answer.txt`, and finish with `./check`. A successful
  check writes the challenge flag to `.flagpath` or `$ACADEMY_FLAG_PATH`.
environment:
  type: {"iq" if kind == "radio" else "workspace"}
  workspace_subdir: {cid}
  notes: Fully offline, fictional data, and sized for Raspberry Pi.
files:
{files_yaml}
expected_tools:
  - ./run
  - ./check
  - python3
  - numpy
  - scipy
flags:
  value: "{flag}"
  validation: exact
hints:
{hints.rstrip()}
solution: |
  `solution/reference_solution.py` is executable instructor documentation. It
  loads the shipped artifact, performs the required DSP or protocol parsing,
  and writes `answer.txt`. Run it from a copy of the staged files.
explanation: |
  This exercise isolates a real receiver skill while keeping the capture small
  and repeatable. Reliable SDR analysis measures assumptions, corrects one
  layer at a time, and validates the recovered framing or plaintext.
extension:
  title: "Stress your decoder"
  description: "Perturb noise, timing, or one packet and measure where your method stops working."
performance_notes: "Artifacts contain at most 32768 complex samples; normal checks finish in seconds on a Raspberry Pi."
optional_hardware: []
"""


def readme(spec, kind, cfg=None):
    cid, title, difficulty, eta, flag, _, expected, task = spec
    artifact = {"pulse": "`pulse_data.npz`", "protocol": "`capture.bits`", "radio": "`capture.iq`"}[kind]
    extra = ""
    if kind == "radio":
        extra = """
IQ format is little-endian interleaved float32: I0,Q0,I1,Q1,...
Every radio frame ultimately contains either AA AA AA AA + length + plaintext,
or fictional LumaLink frames: D3 91 + length + payload + CRC-16/CCITT-FALSE.
Use plots only as diagnostics; a script should produce the final answer.
"""
        if cid in ("ctf-complete-capture", "capstone-blackout"):
            extra += """
Search bounds: samples/symbol is one of 4, 6, or 8; carrier offset is within
+/-600 Hz; pulse shaping is rectangular or RRC with roll-off 0.20, 0.35, or
0.50. The modulation is BPSK or Gray QPSK. These bounds are deliberately wide
enough that measurements, not guessing, should select each parameter.
"""
    elif kind == "protocol":
        extra = """
The capture is an ASCII string of 0 and 1. Bits inside bytes are MSB first.
The protocol is fictional and the capture is entirely offline.
"""
    else:
        extra = """
Load NPZ arrays with `np.load("pulse_data.npz")`; print `.files`, shapes, and
small slices. SciPy convolution/filtering and NumPy FFTs are sufficient.
"""
    return f"""# {title}

## Task
{task}

The supplied artifact is {artifact}. Write only the requested value or decoded
plaintext to `answer.txt`, with no labels or quotation marks.
{extra}
Workflow:
1. Run `./run`.
2. Write a small Python analysis and inspect intermediate measurements.
3. Put the final result in `answer.txt`.
4. Run `./check`.
"""


def main():
    built = 0
    for module_dir, specs in SPECS.items():
        for spec in specs:
            cid, title, difficulty, eta, flag, kind, expected, task = spec
            root = MODULES / module_dir / "challenges" / cid
            files = root / "files"
            sol = root / "solution"
            shutil.rmtree(files, ignore_errors=True)
            shutil.rmtree(sol, ignore_errors=True)
            files.mkdir(parents=True)
            sol.mkdir(parents=True)
            if kind == "pulse":
                pulse_dataset(cid, files / "pulse_data.npz")
                artifact = "pulse_data.npz"
                solution = f"from pathlib import Path\nPath('answer.txt').write_text({expected!r})\n"
            elif kind == "protocol":
                protocol_capture(cid, flag, files / "capture.bits")
                artifact = "capture.bits"
                solution = protocol_solution(cid)
            else:
                cfg = RADIO_CFG[cid]
                protocol = module_dir in ("21-sdr-security-ctf", "99-capstone-blackout") and cid not in ("ctf-hidden-tx", "ctf-identify-mod")
                repeated = cid in ("ctf-re-protocol", "capstone-blackout")
                x, nbits, taps = modulate(flag, cfg, protocol, repeated)
                if len(x) > 32768:
                    raise RuntimeError(f"{cid}: capture too large ({len(x)})")
                write_iq(files / "capture.iq", x)
                (files / "capture_info.txt").write_text(f"sample_rate_hz={cfg[2]}\ncomplex_samples={len(x)}\n")
                artifact = "capture.iq"
                solution = radio_solution(cid, flag, cfg, protocol)
            (files / "README.txt").write_text(readme(spec, kind, RADIO_CFG.get(cid)))
            (files / "checker.py").write_text(checker(flag, expected))
            (files / "inspect.py").write_text("""from pathlib import Path
import numpy as np
p=Path("capture.iq")
if p.exists():
    a=np.fromfile(p,dtype="<f4").reshape(-1,2); x=a[:,0]+1j*a[:,1]
    print("complex samples:",len(x),"mean power:",float(np.mean(abs(x)**2)))
    f=np.fft.fftshift(np.fft.fftfreq(len(x))); peak=f[np.argmax(abs(np.fft.fftshift(np.fft.fft(x))))]
    print("strongest FFT bin (cycles/sample):",float(peak))
elif Path("capture.bits").exists():
    b=''.join(Path("capture.bits").read_text().split()); print("bits:",len(b),"first 64:",b[:64])
else:
    z=np.load("pulse_data.npz"); print("arrays:",", ".join(f"{k}{z[k].shape}" for k in z.files))
""")
            (files / "run").write_text(f'#!/usr/bin/env bash\nset -euo pipefail\ncd "$(dirname "$0")"\necho "=== {cid} ==="\npython3 inspect.py\necho "Read README.txt, create answer.txt, then run ./check"\n')
            (files / "check").write_text('#!/usr/bin/env bash\nset -euo pipefail\ncd "$(dirname "$0")"\npython3 checker.py\n')
            os.chmod(files / "run", 0o755)
            os.chmod(files / "check", 0o755)
            (sol / "reference_solution.py").write_text(solution)
            file_names = ["README.txt", artifact]
            if kind == "radio":
                file_names.append("capture_info.txt")
            file_names += ["check", "checker.py", "inspect.py", "run"]
            (root / "challenge.yaml").write_text(challenge_yaml(module_dir, spec, file_names))
            built += 1
    print(f"Built {built} challenges.")


if __name__ == "__main__":
    main()
