#!/usr/bin/env python3
"""Build the small, deterministic datasets for curriculum modules 12 through 16."""

from __future__ import annotations

import json
import os
from pathlib import Path
import textwrap

import numpy as np
from scipy import signal


ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "curriculum" / "modules"
RNG = np.random.default_rng(12016)
FS = 12_000.0


SPECS = {
    "12-dsp-filters": [
        ("filt-lpf", "Low-pass Filter", "easy", "Keep a low tone and reject a high tone.", "flag{low_pass_leaves_low_tones}"),
        ("filt-hpf", "High-pass Filter", "easy", "Keep a high tone and reject a low tone.", "flag{high_pass_leaves_high_tones}"),
        ("filt-bpf", "Band-pass Filter", "medium", "Isolate one channel between two unwanted tones.", "flag{band_pass_selects_one_channel}"),
        ("filt-fir-design", "Design an FIR Filter", "medium", "Design taps that meet a stated low-pass response.", "flag{fir_taps_shape_the_spectrum}"),
        ("filt-remove-interference", "Remove Narrowband Interference", "medium", "Use a notch filter without damaging nearby content.", "flag{notch_removes_the_interferer}"),
        ("filt-dsp-pipeline", "Build a DSP Pipeline", "hard", "Translate, filter, and decimate a selected channel.", "flag{mix_filter_decimate_pipeline}"),
    ],
    "13-gnu-radio": [
        ("gr-first-flowgraph", "Your First Flowgraph", "easy", "Reproduce a source → gain → sink graph.", "flag{blocks_make_a_signal_flowgraph}"),
        ("gr-fft-flowgraph", "FFT Flowgraph", "easy", "Measure the strongest tone in an IQ stream.", "flag{fft_sink_reveals_the_peak}"),
        ("gr-filtering", "Filtering Flowgraph", "medium", "Implement a low-pass flowgraph offline.", "flag{flowgraph_filter_rejects_noise}"),
        ("gr-freq-xlat", "Frequency Translating FIR", "medium", "Move an offset channel to baseband.", "flag{frequency_translation_centers_channels}"),
        ("gr-recreate-python", "Recreate a Flowgraph in Python", "medium", "Match a documented block chain with NumPy.", "flag{numpy_recreates_the_flowgraph}"),
        ("gr-complete-rx", "Complete a Tiny Receiver", "hard", "Translate, filter, and decode a BPSK message.", "flag{offline_flowgraph_recovers_bits}"),
    ],
    "14-iq-sdr-fundamentals": [
        ("iq-identify", "Identify an IQ Capture", "easy", "Recognize interleaved float32 I/Q samples.", "flag{iq_is_in_phase_and_quadrature}"),
        ("iq-complex-analysis", "Complex IQ Analysis", "easy", "Measure magnitude, phase, and mean power.", "flag{complex_samples_encode_phase}"),
        ("iq-find-signal", "Find a Signal in Spectrum", "medium", "Locate a hidden narrowband signal.", "flag{fft_finds_hidden_iq_energy}"),
        ("iq-bandwidth", "Estimate Occupied Bandwidth", "medium", "Estimate a signal's occupied bandwidth.", "flag{bandwidth_measures_spectral_width}"),
        ("iq-recover-baseband", "Recover Baseband", "medium", "Estimate an offset and mix the signal to zero hertz.", "flag{complex_mixing_recovers_baseband}"),
        ("iq-unknown-capture", "Unknown Capture", "hard", "Infer sample rate, offset, and modulation from evidence.", "flag{unknown_iq_yields_to_measurement}"),
    ],
    "15-bpsk": [
        ("bpsk-identify", "Identify BPSK", "easy", "Recognize the two opposite BPSK constellation points.", "flag{bpsk_has_two_opposite_symbols}"),
        ("bpsk-decode-clean", "Decode Clean BPSK", "easy", "Map clean symbols to bits and ASCII.", "flag{bpsk_clean_decode}"),
        ("bpsk-noise", "BPSK through Noise", "medium", "Average noisy samples before making bit decisions.", "flag{bpsk_averaging_beats_noise}"),
        ("bpsk-mapping", "Discover BPSK Mapping", "medium", "Resolve whether positive real means zero or one.", "flag{bpsk_mapping_from_preamble}"),
        ("bpsk-phase", "Correct BPSK Phase", "medium", "Estimate and remove a constant carrier phase.", "flag{bpsk_phase_rotation_corrected}"),
        ("bpsk-phase-freq", "Correct BPSK Phase and Frequency", "hard", "Estimate frequency drift and phase before decoding.", "flag{bpsk_carrier_offset_removed}"),
    ],
    "16-qpsk": [
        ("qpsk-constellation", "Read a QPSK Constellation", "easy", "Recognize four QPSK symbol quadrants.", "flag{qpsk_carries_two_bits_per_symbol}"),
        ("qpsk-decode-clean", "Decode Clean QPSK", "easy", "Decode Gray-mapped QPSK into ASCII.", "flag{qpsk_clean_decode}"),
        ("qpsk-gray", "Learn Gray Mapping", "medium", "Infer quadrant labels from a known preamble.", "flag{gray_neighbors_differ_by_one_bit}"),
        ("qpsk-noise", "QPSK through Noise", "medium", "Average noisy QPSK symbols before slicing.", "flag{qpsk_cluster_centers_survive_noise}"),
        ("qpsk-phase", "Correct QPSK Phase", "medium", "Remove an unknown constant QPSK phase.", "flag{qpsk_fourth_power_finds_phase}"),
        ("qpsk-freq", "QPSK with Frequency Offset", "hard", "Estimate frequency and phase offsets, then decode.", "flag{qpsk_frequency_offset_corrected}"),
    ],
}


def interleave(x: np.ndarray) -> np.ndarray:
    return np.column_stack((x.real, x.imag)).astype("<f4").ravel()


def write_iq(path: Path, x: np.ndarray) -> None:
    interleave(x).tofile(path)


def tone(freq: float, n: int, fs: float = FS, phase: float = 0.0) -> np.ndarray:
    return np.exp(1j * (2 * np.pi * freq * np.arange(n) / fs + phase))


def bits_for(text: str) -> np.ndarray:
    return np.unpackbits(np.frombuffer(text.encode("ascii"), dtype=np.uint8))


def bpsk_wave(text: str, sps: int, phase=0.0, cfo=0.0, noise=0.0) -> np.ndarray:
    symbols = 1 - 2 * bits_for(text).astype(float)
    x = np.repeat(symbols, sps).astype(complex)
    x *= np.exp(1j * (phase + 2 * np.pi * cfo * np.arange(x.size) / FS))
    if noise:
        x += noise * (RNG.normal(size=x.size) + 1j * RNG.normal(size=x.size))
    return x.astype(np.complex64)


QMAP = {(0, 0): 1 + 1j, (0, 1): -1 + 1j, (1, 1): -1 - 1j, (1, 0): 1 - 1j}


def qpsk_wave(text: str, sps: int, phase=0.0, cfo=0.0, noise=0.0) -> np.ndarray:
    b = bits_for(text)
    symbols = np.array([QMAP[tuple(pair)] for pair in b.reshape(-1, 2)]) / np.sqrt(2)
    x = np.repeat(symbols, sps)
    x *= np.exp(1j * (phase + 2 * np.pi * cfo * np.arange(x.size) / FS))
    if noise:
        x += noise * (RNG.normal(size=x.size) + 1j * RNG.normal(size=x.size))
    return x.astype(np.complex64)


def yaml_for(module: str, cid: str, title: str, difficulty: str, goal: str, flag: str, files: list[str]) -> str:
    minutes = {"easy": "20-40 minutes", "medium": "40-75 minutes", "hard": "60-120 minutes"}[difficulty]
    kind = "flowgraph" if module == "gnu-radio" else ("iq" if module in {"iq-sdr-fundamentals", "bpsk", "qpsk"} else "workspace")
    gr_note = ""
    if module == "gnu-radio":
        gr_note = """
  GNU Radio is optional. The primary path uses NumPy/SciPy and works on the
  offline Pi image. If GNU Radio Companion is installed, `optional.grc`
  provides the equivalent block layout to explore."""
    listed = "\n".join(f"  - {name}" for name in files)
    return f"""id: {cid}
module: {module}
title: "{title}"
difficulty: {difficulty}
estimated_time: "{minutes}"
prerequisites: []
objectives:
  - inspect_iq_data
  - implement_a_small_dsp_step
  - verify_the_result
mastery_evidence:
  - understand
  - implement
  - apply
description: |
  ## Mission
  {goal}

  Digital signal processing (DSP) changes or measures sampled signals with
  arithmetic. IQ samples are complex numbers: I is the real (in-phase) part
  and Q is the imaginary (quadrature) part. Read `README.txt`, then run
  `./run`. It reports the exact deliverable and useful starter measurements.
  Finish by running `./check`; a correct result writes the flag to `.flagpath`
  (or `ACADEMY_FLAG_PATH`, with `/home/flag.txt` as the Pi fallback).{gr_note}
environment:
  type: {kind}
  workspace_subdir: {cid}
  notes: Fully offline, software-only, and sized for Raspberry Pi.
files:
{listed}
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
  - level: 1
    text: "Run ./run and inspect README.txt. Start with the printed sample count and spectrum."
  - level: 2
    text: "Load IQ with np.fromfile(..., dtype='<f4').reshape(-1, 2), then use a[:,0] + 1j*a[:,1]."
  - level: 3
    text: "Use np.fft.fftfreq/fftshift for frequency; average all samples in one symbol before slicing."
  - level: 4
    text: "Build the solution one measured stage at a time; the instructor reference uses fewer than 25 lines of Python."
solution: |
  The challenge's hidden `solution/reference_solution.py` is executable
  documentation. Run it from a copy of the staged files, inspect the generated
  answer or output, and then run `./check`. It shows a compact NumPy/SciPy
  implementation and comments the important DSP operation.
explanation: |
  {goal} The key habit is to verify every stage numerically: inspect the
  spectrum, apply one operation, and measure again. This is the same workflow
  used for live SDR receivers, only with a short repeatable capture.
extension:
  title: "Stress the receiver"
  description: "Change one parameter in a copy of the generator or add noise, then find where your method fails."
performance_notes: "Captures contain fewer than 200,000 complex float32 samples and checks normally finish in seconds."
optional_hardware: []
"""


COMMON_PY = """\
from pathlib import Path
import os
import numpy as np
from scipy import signal

def load_iq(name="capture.iq"):
    a = np.fromfile(name, dtype="<f4").reshape(-1, 2)
    return a[:, 0] + 1j * a[:, 1]

def write_iq(name, x):
    np.column_stack((x.real, x.imag)).astype("<f4").tofile(name)

def flag_path():
    marker = Path(".flagpath")
    if marker.is_file():
        return Path(marker.read_text().strip())
    return Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
"""


def shell_files(files: Path, cid: str) -> None:
    run = f"""#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "=== {cid} ==="
python3 inspect_capture.py
echo
echo "Read README.txt, create the requested answer/output, then run ./check"
"""
    (files / "run").write_text(run)
    (files / "check").write_text("#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")\"\npython3 checker.py\n")
    os.chmod(files / "run", 0o755)
    os.chmod(files / "check", 0o755)


def checker(files: Path, flag: str, body: str) -> None:
    code = COMMON_PY + "\nFLAG = " + repr(flag) + "\n\n"
    code += "def fail(message):\n    print('Not correct yet: ' + message)\n    raise SystemExit(1)\n\n"
    code += textwrap.dedent(body)
    code += """
out = flag_path()
try:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(FLAG + "\\n")
    print("Correct! Flag written to:", out)
except OSError:
    print(FLAG)
"""
    (files / "checker.py").write_text(code)


def inspect_script(files: Path, fs: float | None, extra: str = "") -> None:
    text = COMMON_PY + "\n"
    if (files / "capture.iq").exists():
        text += """x = load_iq()
print(f"capture.iq: {len(x)} complex samples ({8*len(x)} bytes)")
print(f"mean power: {np.mean(np.abs(x)**2):.4f}")
"""
        if fs:
            text += f"""fs = {fs!r}
spec = np.abs(np.fft.fftshift(np.fft.fft(x)))
freq = np.fft.fftshift(np.fft.fftfreq(len(x), 1/fs))
print(f"strongest FFT bin: {{freq[np.argmax(spec)]:.1f}} Hz")
"""
    text += textwrap.dedent(extra)
    (files / "inspect_capture.py").write_text(text)


def readme(files: Path, title: str, task: str, notes: str = "") -> None:
    (files / "README.txt").write_text(f"""# {title}

{task}

IQ files use little-endian interleaved float32 values: I0,Q0,I1,Q1,...
`sample_rate.txt` gives samples/second when provided. A finite impulse response
(FIR) filter is simply convolution with a short list of coefficients (taps).
{notes}

Workflow:
1. `./run`
2. Write a small Python solution or edit the requested answer file.
3. `./check`
""")


def filter_challenge(files: Path, cid: str, title: str, flag: str) -> None:
    n = 12_000
    t = np.arange(n) / FS
    if cid == "filt-lpf":
        x = tone(350, n) + 0.8 * tone(3_200, n)
        task = "Create `output.npy`, same length as `input.npy`, retaining 350 Hz and attenuating 3200 Hz by at least 20 dB. Use a low-pass filter."
        snippet = """
y = np.load("output.npy")
if y.shape != x.shape: fail("output.npy must have the same shape as input.npy")
def amp(z, f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/fs), z))/len(z)
if amp(y,350) < .55*amp(x,350): fail("350 Hz was attenuated too much")
if amp(y,3200) > .1*amp(x,3200): fail("3200 Hz needs at least 20 dB attenuation")
"""
        sol = "x=np.load('input.npy'); taps=signal.firwin(101,1000,fs=12000); np.save('output.npy',signal.lfilter(taps,1,x))"
    elif cid == "filt-hpf":
        x = tone(300, n) + 0.8 * tone(3_000, n)
        task = "Create `output.npy` retaining 3000 Hz and attenuating 300 Hz by at least 20 dB. Use a high-pass filter."
        snippet = """
y=np.load("output.npy")
if y.shape != x.shape: fail("output.npy must have the same shape as input.npy")
def amp(z,f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/fs),z))/len(z)
if amp(y,3000)<.55*amp(x,3000): fail("3000 Hz was attenuated too much")
if amp(y,300)>.1*amp(x,300): fail("300 Hz needs at least 20 dB attenuation")
"""
        sol = "x=np.load('input.npy'); taps=signal.firwin(101,1500,pass_zero=False,fs=12000); np.save('output.npy',signal.lfilter(taps,1,x))"
    elif cid == "filt-bpf":
        x = tone(300, n) + tone(1_800, n) + tone(3_800, n)
        task = "Create `output.npy` retaining 1800 Hz while attenuating 300 Hz and 3800 Hz by at least 20 dB."
        snippet = """
y=np.load("output.npy")
if y.shape != x.shape: fail("output.npy must have the same shape as input.npy")
def amp(z,f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/fs),z))/len(z)
if amp(y,1800)<.5*amp(x,1800): fail("1800 Hz was attenuated too much")
if max(amp(y,300)/amp(x,300),amp(y,3800)/amp(x,3800))>.1: fail("both unwanted tones need 20 dB attenuation")
"""
        sol = "x=np.load('input.npy'); taps=signal.firwin(151,[1200,2400],pass_zero=False,fs=12000); np.save('output.npy',signal.lfilter(taps,1,x))"
    elif cid == "filt-fir-design":
        x = np.zeros(n, dtype=np.complex64)
        task = "Create `taps.npy`: 41 to 161 real FIR taps, passband through 900 Hz (loss < 3 dB), and stopband from 1800 Hz (attenuation > 25 dB)."
        snippet = """
t=np.load("taps.npy")
if t.ndim!=1 or not 41<=len(t)<=161 or np.max(np.abs(np.imag(t)))>1e-8: fail("use 41..161 real taps")
w,h=signal.freqz(np.real(t),worN=8192,fs=fs)
pb=np.abs(h[w<=900]); sb=np.abs(h[w>=1800])
if pb.min()<10**(-3/20) or pb.max()>10**(3/20): fail("passband must stay within 3 dB")
if sb.max()>10**(-25/20): fail("stopband needs 25 dB attenuation")
"""
        sol = "np.save('taps.npy',signal.firwin(101,1300,fs=12000,window=('kaiser',5.0)))"
    elif cid == "filt-remove-interference":
        x = tone(700, n) + 2.5 * tone(1_500, n) + tone(2_300, n)
        task = "Create `output.npy` with a narrow notch at 1500 Hz. Reduce it by 25 dB while keeping 700 and 2300 Hz within 3 dB."
        snippet = """
y=np.load("output.npy")
if y.shape!=x.shape: fail("output.npy shape is wrong")
def amp(z,f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/fs),z))/len(z)
if amp(y,1500)/amp(x,1500)>10**(-25/20): fail("1500 Hz interferer remains")
for f in (700,2300):
    if amp(y,f)/amp(x,f)<10**(-3/20): fail(f"{f} Hz desired tone was damaged")
"""
        sol = "x=np.load('input.npy'); b,a=signal.iirnotch(1500,30,fs=12000); np.save('output.npy',signal.lfilter(b,a,x))"
    else:
        x = tone(2_400, n) + 0.7 * tone(-2_800, n)
        task = "Select the +2400 Hz channel: mix it to 0 Hz, low-pass below 500 Hz, decimate by 4, and save 3000 complex samples as `output.npy`."
        snippet = """
y=np.load("output.npy")
if y.ndim!=1 or len(y)!=3000: fail("output.npy must contain 3000 samples")
if abs(np.mean(y))<.55: fail("selected channel is not centered/retained")
if np.std(y[100:])>.2: fail("unwanted channel remains after filtering and decimation")
"""
        sol = "x=np.load('input.npy'); n=np.arange(len(x)); z=x*np.exp(-2j*np.pi*2400*n/12000); taps=signal.firwin(129,500,fs=12000); np.save('output.npy',signal.lfilter(taps,1,z)[::4])"
    np.save(files / "input.npy", x.astype(np.complex64))
    (files / "sample_rate.txt").write_text("12000\n")
    readme(files, title, task)
    (files / "reference_solution.py").write_text("import numpy as np\nfrom scipy import signal\n" + sol + "\n")
    checker(files, flag, "x=np.load('input.npy'); fs=12000.0\n" + snippet)
    inspect_script(files, None, """x=np.load("input.npy")
print("input.npy:", x.shape, x.dtype)
print("sample rate: 12000 Hz")
""")


def gr_challenge(files: Path, cid: str, title: str, flag: str) -> None:
    n = 12_000
    x = (tone(700, n) + .6 * tone(3_200, n)).astype(np.complex64)
    task = ""
    if cid == "gr-first-flowgraph":
        np.save(files / "input.npy", x)
        task = "Model File Source → Multiply Const(0.5) → File Sink. Save the complex result as `output.npy`."
        sol = "np.save('output.npy',np.load('input.npy')*0.5)"
        body = """x=np.load("input.npy"); y=np.load("output.npy")
if y.shape!=x.shape or not np.allclose(y,.5*x,rtol=1e-5,atol=1e-6): fail("output does not match a gain of 0.5")
"""
    elif cid == "gr-fft-flowgraph":
        write_iq(files / "capture.iq", tone(1_375, n) + .25 * tone(-2200, n))
        task = "Write the strongest FFT frequency, in Hz, to `answer.txt` as one number (tolerance ±3 Hz)."
        sol = "x=load_iq(); f=np.fft.fftfreq(len(x),1/12000); Path('answer.txt').write_text(str(f[np.argmax(abs(np.fft.fft(x)))]))"
        body = """try: a=float(Path("answer.txt").read_text())
except Exception: fail("answer.txt must contain one number")
if abs(a-1375)>3: fail("the peak frequency is not correct")
"""
    elif cid == "gr-filtering":
        write_iq(files / "capture.iq", x)
        task = "Low-pass `capture.iq` at 1200 Hz and save interleaved float32 IQ as `output.iq`; keep 700 Hz and reject 3200 Hz by 20 dB."
        sol = "x=load_iq(); write_iq('output.iq',signal.lfilter(signal.firwin(101,1200,fs=12000),1,x))"
        body = """x=load_iq(); y=load_iq("output.iq")
if len(y)!=len(x): fail("output.iq length differs from capture")
def amp(z,f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/12000),z))/len(z)
if amp(y,700)<.5*amp(x,700) or amp(y,3200)>.1*amp(x,3200): fail("filter response misses the target")
"""
    elif cid == "gr-freq-xlat":
        write_iq(files / "capture.iq", tone(2_100, n))
        task = "Frequency-translate the +2100 Hz tone to 0 Hz and save it as `output.iq`."
        sol = "x=load_iq(); n=np.arange(len(x)); write_iq('output.iq',x*np.exp(-2j*np.pi*2100*n/12000))"
        body = """y=load_iq("output.iq")
if len(y)!=12000: fail("output length is wrong")
phase_step=np.angle(np.mean(y[1:]*np.conj(y[:-1])))
if abs(phase_step*12000/(2*np.pi))>5 or abs(np.mean(y))<.8: fail("channel is not centered at DC")
"""
    elif cid == "gr-recreate-python":
        np.save(files / "input.npy", x)
        task = "Recreate: Multiply Const(0.25) → FIR low-pass(1200 Hz, 101 taps) → keep every second sample. Save `output.npy`."
        sol = "x=np.load('input.npy'); t=signal.firwin(101,1200,fs=12000); np.save('output.npy',signal.lfilter(t,1,.25*x)[::2])"
        body = """x=np.load("input.npy"); y=np.load("output.npy")
ref=signal.lfilter(signal.firwin(101,1200,fs=12000),1,.25*x)[::2]
if y.shape!=ref.shape or not np.allclose(y,ref,rtol=2e-4,atol=2e-5): fail("output does not match the documented chain")
"""
    else:
        msg = flag
        base = bpsk_wave(msg, 8)
        x = base * tone(1_500, len(base))
        write_iq(files / "capture.iq", x)
        task = "Complete the receiver: mix -1500 Hz, average each 8-sample symbol, decide real>0 as bit 0, pack bits MSB-first, and write decoded ASCII to `answer.txt`."
        sol = "x=load_iq(); n=np.arange(len(x)); z=x*np.exp(-2j*np.pi*1500*n/12000); s=z.reshape(-1,8).mean(1); b=(s.real<0).astype(np.uint8); Path('answer.txt').write_text(np.packbits(b).tobytes().decode())"
        body = f"""try: text=Path("answer.txt").read_text().strip()
except Exception: fail("missing answer.txt")
if text!={flag!r}: fail("decoded ASCII is not correct")
"""
    readme(files, title, task, "GNU Radio Companion is optional; `optional.grc` sketches the same blocks.")
    (files / "reference_solution.py").write_text(COMMON_PY + "\n" + sol + "\n")
    (files / "optional.grc").write_text("""<?xml version="1.0"?>
<flow_graph><timestamp>offline teaching sketch</timestamp><block><key>options</key></block>
<block><key>blocks_file_source</key></block><block><key>processing_block</key></block>
<block><key>blocks_file_sink</key></block></flow_graph>
""")
    checker(files, flag, body)
    inspect_script(files, FS if (files / "capture.iq").exists() else None, """p=Path("input.npy")
if p.exists():
    x=np.load(p); print("input.npy:",len(x),"complex samples")
print("Primary path: NumPy/SciPy. Optional path: open optional.grc in GNU Radio Companion.")
""")


def iq_challenge(files: Path, cid: str, title: str, flag: str) -> None:
    n = 16_384
    task = ""
    if cid == "iq-identify":
        x = .8 * tone(750, 4096)
        expected = "complex64"
        task = "Inspect `capture.iq`. Write `complex64` to `answer.txt` after identifying how pairs of float32 values become one complex sample."
    elif cid == "iq-complex-analysis":
        x = .5 * tone(600, 6000, phase=np.pi/6)
        expected = "0.25"
        task = "Compute mean power `mean(abs(x)**2)` and write it to `answer.txt` (tolerance ±0.01)."
    elif cid == "iq-find-signal":
        x = .15 * (RNG.normal(size=n) + 1j * RNG.normal(size=n)) + tone(-2_250, n)
        expected = "-2250"
        task = "Find the strongest FFT frequency and write it in Hz to `answer.txt` (tolerance ±5 Hz)."
    elif cid == "iq-bandwidth":
        # Deterministic band-limited noise, approximately 1200 Hz occupied width.
        raw = RNG.normal(size=n) + 1j * RNG.normal(size=n)
        x = signal.lfilter(signal.firwin(257, 600, fs=FS), 1, raw)
        expected = "1200"
        task = "Estimate the two-sided occupied bandwidth. Write Hz to `answer.txt`; values from 1000 through 1400 pass."
    elif cid == "iq-recover-baseband":
        x = tone(1_850, n) * (1 + .2 * np.sin(2*np.pi*70*np.arange(n)/FS))
        expected = "1850"
        task = "Estimate the carrier offset needed to move the signal to baseband. Write the positive offset in Hz to `answer.txt` (±5 Hz)."
    else:
        # No sample-rate sidecar by design. A metadata clue plus periodicity makes it inferable.
        x = qpsk_wave("TRAINING", 8, cfo=900)
        expected = "12000,900,qpsk"
        task = "No sample-rate sidecar is supplied. `receiver_note.txt` gives one timing clue. Write `sample_rate_hz,carrier_hz,modulation` to `answer.txt`."
        (files / "receiver_note.txt").write_text("Front-end decimation output was configured for 12 ksamples/s; symbol period is 8 samples.\n")
    write_iq(files / "capture.iq", x)
    if cid != "iq-unknown-capture":
        (files / "sample_rate.txt").write_text("12000\n")
    readme(files, title, task, "Positive FFT frequency means counter-clockwise complex rotation.")
    if cid == "iq-identify":
        sol = "Path('answer.txt').write_text('complex64')"
        body = """try: a=Path("answer.txt").read_text().strip().lower()
except Exception: fail("missing answer.txt")
if a!="complex64": fail("identify the complex sample representation")
"""
    elif cid == "iq-bandwidth":
        sol = "Path('answer.txt').write_text('1200')"
        body = """try: a=float(Path("answer.txt").read_text())
except Exception: fail("answer must be numeric Hz")
if not 1000<=a<=1400: fail("bandwidth is outside the accepted estimate")
"""
    elif cid == "iq-unknown-capture":
        sol = "Path('answer.txt').write_text('12000,900,qpsk')"
        body = """try: p=[v.strip().lower() for v in Path("answer.txt").read_text().split(",")]
except Exception: fail("missing answer.txt")
if len(p)!=3 or p[2]!="qpsk": fail("format is sample_rate,carrier,modulation")
try: fs,fc=float(p[0]),float(p[1])
except ValueError: fail("sample rate and carrier must be numbers")
if abs(fs-12000)>1 or abs(fc-900)>10: fail("one or more estimated parameters is wrong")
"""
    else:
        value = float(expected)
        tolerance = .01 if cid == "iq-complex-analysis" else 5
        sol = f"Path('answer.txt').write_text({expected!r})"
        body = f"""try: a=float(Path("answer.txt").read_text())
except Exception: fail("answer.txt must contain one number")
if abs(a-{value})>{tolerance}: fail("measurement is outside tolerance")
"""
    (files / "reference_solution.py").write_text(COMMON_PY + "\n" + sol + "\n")
    checker(files, flag, body)
    inspect_script(files, None if cid == "iq-unknown-capture" else FS)


def modulation_challenge(files: Path, module: str, cid: str, title: str, flag: str) -> None:
    is_q = module == "qpsk"
    sps = 8
    if cid.endswith("identify") or cid.endswith("constellation"):
        text = "four" if is_q else "two"
        x = qpsk_wave("ABCD", sps) if is_q else bpsk_wave("ABCD", sps)
        task = f"Count the ideal constellation clusters after averaging each {sps}-sample symbol. Write `{text}` to `answer.txt`."
        sol = f"Path('answer.txt').write_text({text!r})"
        body = f"""try: a=Path("answer.txt").read_text().strip().lower()
except Exception: fail("missing answer.txt")
if a!={text!r}: fail("constellation cluster count is wrong")
"""
    else:
        msg = flag
        phase = 0.0
        cfo = 0.0
        noise = 0.0
        if cid.endswith("noise"):
            noise = .65 if is_q else .8
        if cid.endswith("phase"):
            phase = .43 if is_q else .71
        if cid.endswith("phase-freq"):
            phase, cfo = .55, 37.0
        if cid.endswith("freq"):
            phase, cfo = .31, 31.0
        x = qpsk_wave(msg, sps, phase, cfo, noise) if is_q else bpsk_wave(msg, sps, phase, cfo, noise)
        task = f"Decode the {sps}-samples/symbol capture and write the recovered ASCII flag to `answer.txt`."
        if "mapping" in cid or "gray" in cid:
            task += " `preamble.txt` states the known first bytes so you can resolve the symbol-to-bit mapping."
            (files / "preamble.txt").write_text("The message begins with ASCII: flag{\n")
        sol = modulation_solution(is_q, phase != 0.0, cfo != 0.0)
        body = f"""try: a=Path("answer.txt").read_text().strip()
except Exception: fail("missing answer.txt")
if a!={flag!r}: fail("decoded text is not the transmitted flag")
"""
    write_iq(files / "capture.iq", x)
    (files / "sample_rate.txt").write_text("12000\n")
    (files / "symbol_rate.txt").write_text("1500\n")
    readme(files, title, task, "Average each group of 8 samples first. Packing is MSB-first (`np.packbits`).")
    (files / "reference_solution.py").write_text(COMMON_PY + "\n" + sol + "\n")
    checker(files, flag, body)
    inspect_script(files, FS, f"""print("symbol rate: 1500 symbols/s; samples/symbol: {sps}")
""")


def modulation_solution(is_q: bool, phase: bool, cfo: bool) -> str:
    lines = ["x=load_iq()", "sps=8"]
    if cfo:
        power = 4 if is_q else 2
        lines += [
            f"# The {power}th power removes data modulation; its phase slope reveals CFO.",
            f"p=np.unwrap(np.angle(x**{power}))",
            f"cfo=np.polyfit(np.arange(len(x)),p,1)[0]*12000/(2*np.pi*{power})",
            "x=x*np.exp(-2j*np.pi*cfo*np.arange(len(x))/12000)",
        ]
    lines += ["s=x.reshape(-1,sps).mean(1)"]
    if (phase or cfo) and not is_q:
        power = 4 if is_q else 2
        lines += [
            f"phi=np.angle(np.mean(s**{power}))/{power}",
            "s=s*np.exp(-1j*phi)",
        ]
    if is_q:
        if phase or cfo:
            lines += [
                "# Fourth-power phase has a 90-degree ambiguity; known ASCII resolves it.",
                "raw=np.angle(np.mean(s**4))/4-np.pi/4",
                "text=None",
                "for k in range(4):",
                "    r=s*np.exp(-1j*(raw+k*np.pi/2))",
                "    bits=np.column_stack((r.imag<0,r.real<0)).astype(np.uint8).ravel()",
                "    candidate=np.packbits(bits).tobytes().decode('ascii',errors='ignore')",
                "    if candidate.startswith('flag{'): text=candidate; break",
                "if text is None: raise RuntimeError('could not resolve QPSK quadrant ambiguity')",
                "Path('answer.txt').write_text(text)",
                "raise SystemExit(0)",
            ]
        else:
            lines += ["bits=np.column_stack((s.imag<0,s.real<0)).astype(np.uint8).ravel()"]
    else:
        lines += ["bits=(s.real<0).astype(np.uint8)"]
    lines += ["Path('answer.txt').write_text(np.packbits(bits).tobytes().decode('ascii'))"]
    return "\n".join(lines)


def build() -> None:
    for module_dir, entries in SPECS.items():
        module = module_dir.split("-", 1)[1]
        for cid, title, difficulty, goal, flag in entries:
            root = MODULES / module_dir / "challenges" / cid
            files = root / "files"
            files.mkdir(parents=True, exist_ok=True)
            for old in files.iterdir():
                if old.is_file():
                    old.unlink()
            shell_files(files, cid)
            if module == "dsp-filters":
                filter_challenge(files, cid, title, flag)
            elif module == "gnu-radio":
                gr_challenge(files, cid, title, flag)
            elif module == "iq-sdr-fundamentals":
                iq_challenge(files, cid, title, flag)
            else:
                modulation_challenge(files, module, cid, title, flag)
            solution_dir = root / "solution"
            solution_dir.mkdir(exist_ok=True)
            for old in solution_dir.iterdir():
                if old.is_file():
                    old.unlink()
            (files / "reference_solution.py").replace(solution_dir / "reference_solution.py")
            names = sorted(p.name for p in files.iterdir() if p.is_file())
            (root / "challenge.yaml").write_text(yaml_for(module, cid, title, difficulty, goal, flag, names))
    print("Built", sum(map(len, SPECS.values())), "challenges")


if __name__ == "__main__":
    build()
