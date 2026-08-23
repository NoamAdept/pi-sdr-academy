#!/usr/bin/env python3
"""Generate curriculum module stubs and challenge scaffolds from the master outline."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "curriculum" / "modules"

MODULES = [
    {
        "order": 0,
        "slug": "orientation",
        "dir": "00-orientation",
        "title": "Raspberry Pi / Debian Orientation",
        "description": "Learn the terminal, filesystem, permissions, processes, and basic system investigation on Debian.",
        "prerequisites": [],
        "challenges": [
            ("orient-find-flag", "easy", "Find the Flag", "15-30 minutes",
             ["terminal", "filesystem", "pwd", "ls", "cd", "find", "cat"]),
            ("orient-permissions", "easy", "Permissions", "20-45 minutes",
             ["users", "groups", "permissions", "chmod"]),
            ("orient-process-hunt", "medium", "Process Hunt", "1-2 hours",
             ["ps", "proc", "process-launch"]),
            ("orient-environment", "medium", "Environment", "1-2 hours",
             ["env", "environment-variables"]),
            ("orient-broken-service", "hard", "Broken Service", "2-4 hours",
             ["systemd-or-local-service", "logs", "diagnosis"]),
            ("orient-system-investigation", "hard", "System Investigation", "3-5 hours",
             ["proc", "logs", "permissions", "networking"]),
        ],
    },
    {
        "order": 1,
        "slug": "linux-cli",
        "dir": "01-linux-cli",
        "title": "Linux Command Line",
        "description": "Master pipelines, text extraction, log analysis, and Bash automation.",
        "prerequisites": ["orientation"],
        "challenges": [
            ("cli-pipeline", "easy", "Pipeline", "20-45 minutes", ["pipes", "unix-tools"]),
            ("cli-text-extraction", "easy", "Text Extraction", "20-45 minutes", ["grep", "find", "cut"]),
            ("cli-log-detective", "medium", "Log Detective", "1-2 hours", ["logs", "awk", "sort"]),
            ("cli-shell-automation", "medium", "Shell Automation", "1-3 hours", ["bash", "scripting"]),
            ("cli-multistage-pipeline", "hard", "Multi-stage Pipeline", "2-4 hours",
             ["grep", "awk", "sed", "sort", "uniq", "pipes"]),
            ("cli-build-tool", "hard", "Build Your Own Tool", "3-5 hours", ["bash", "investigation"]),
        ],
    },
    {
        "order": 2,
        "slug": "python",
        "dir": "02-python",
        "title": "Python",
        "description": "Python fundamentals through binary formats, sockets, and automated analysis.",
        "prerequisites": ["linux-cli"],
        "challenges": [
            ("py-control-flow", "easy", "Variables and Control Flow", "20-40 minutes", ["python-basics"]),
            ("py-file-parser", "easy", "File Parser", "30-60 minutes", ["files", "parsing"]),
            ("py-binary-decoder", "medium", "Binary Decoder", "1-2 hours", ["struct", "binary"]),
            ("py-socket-client", "medium", "Socket Client", "1-2 hours", ["sockets", "local-server"]),
            ("py-protocol-parser", "hard", "Protocol Parser", "2-4 hours", ["protocol-re"]),
            ("py-auto-investigator", "hard", "Automated Investigator", "3-5 hours", ["tooling", "datasets"]),
        ],
    },
    {
        "order": 3,
        "slug": "c",
        "dir": "03-c",
        "title": "C",
        "description": "Compile, pointers, memory layout, and debugging C without advanced exploitation.",
        "prerequisites": ["python"],
        "challenges": [
            ("c-compile-it", "easy", "Compile It", "15-30 minutes", ["gcc", "make"]),
            ("c-pointer-basics", "easy", "Pointer Basics", "30-60 minutes", ["pointers"]),
            ("c-memory-layout", "medium", "Memory Layout", "1-2 hours", ["stack", "heap", "segments"]),
            ("c-binary-parser", "medium", "Binary File Parser", "1-3 hours", ["fread", "structs"]),
            ("c-debug-crash", "hard", "Debug the Crash", "2-4 hours", ["gdb", "segfault"]),
            ("c-re-datastruct", "hard", "Reverse Engineer the Data Structure", "3-5 hours",
             ["memory", "structs"]),
        ],
    },
    {
        "order": 4,
        "slug": "debugging-gdb",
        "dir": "04-debugging-gdb",
        "title": "Debugging / GDB",
        "description": "Breakpoints, watchpoints, stack frames, sanitizers, and core dumps.",
        "prerequisites": ["c"],
        "challenges": [
            ("gdb-first-breakpoint", "easy", "First Breakpoint", "20-40 minutes", ["gdb", "breakpoints"]),
            ("gdb-find-variable", "easy", "Find the Variable", "30-60 minutes", ["print", "examine"]),
            ("gdb-follow-stack", "medium", "Follow the Stack", "1-2 hours", ["backtrace", "frames"]),
            ("gdb-inspect-memory", "medium", "Inspect Memory", "1-2 hours", ["x/", "registers"]),
            ("gdb-segfault", "hard", "Debug the Segmentation Fault", "2-4 hours", ["segfault", "asan"]),
            ("gdb-logic-bug", "hard", "Find the Logic Bug", "3-5 hours", ["conditional-bp", "watchpoints"]),
        ],
    },
    {
        "order": 5,
        "slug": "cpp",
        "dir": "05-cpp",
        "title": "C++",
        "description": "Modern C++: classes, STL, RAII, smart pointers, and library design.",
        "prerequisites": ["debugging-gdb"],
        "challenges": [
            ("cpp-first-class", "easy", "First Class", "20-45 minutes", ["classes"]),
            ("cpp-stl", "easy", "STL Investigation", "30-60 minutes", ["stl", "containers"]),
            ("cpp-raii", "medium", "RAII", "1-2 hours", ["raii", "resources"]),
            ("cpp-smart-ptr", "medium", "Smart Pointer Debugging", "1-3 hours", ["unique_ptr", "shared_ptr"]),
            ("cpp-mini-lib", "hard", "Build a Mini Library", "3-5 hours", ["headers", "api-design"]),
            ("cpp-debug-app", "hard", "Debug a C++ Application", "3-5 hours", ["gdb", "cpp"]),
        ],
    },
    {
        "order": 6,
        "slug": "cmake",
        "dir": "06-cmake",
        "title": "CMake",
        "description": "Professional multi-file C++ builds with libraries, CTest, and dependency debugging.",
        "prerequisites": ["cpp"],
        "challenges": [
            ("cmake-first", "easy", "First CMake Project", "20-40 minutes", ["cmake"]),
            ("cmake-targets", "easy", "Multiple Targets", "30-60 minutes", ["targets"]),
            ("cmake-static-lib", "medium", "Static Library", "1-2 hours", ["add_library"]),
            ("cmake-ctest", "medium", "Tests with CTest", "1-2 hours", ["ctest"]),
            ("cmake-multidir", "hard", "Multi-directory Project", "2-4 hours", ["add_subdirectory"]),
            ("cmake-dep-debug", "hard", "Dependency / Build Debugging", "3-5 hours", ["find_package"]),
        ],
    },
    {
        "order": 7,
        "slug": "git-workflow",
        "dir": "07-git-workflow",
        "title": "Git / Engineering Workflow",
        "description": "Local Git workflows: commits, recovery, branches, merges, and history repair.",
        "prerequisites": ["linux-cli"],
        "challenges": [
            ("git-first-repo", "easy", "First Repository", "15-30 minutes", ["git-init", "commit"]),
            ("git-commit-invest", "easy", "Commit Investigation", "20-45 minutes", ["git-log", "show"]),
            ("git-recover-deleted", "medium", "Recover Deleted Work", "1-2 hours", ["reflog", "checkout"]),
            ("git-branch-merge", "medium", "Branch/Merge Challenge", "1-3 hours", ["branch", "merge"]),
            ("git-debug-history", "hard", "Debug Using Git History", "2-4 hours", ["bisect", "blame"]),
            ("git-repair-history", "hard", "Repair a Broken Project History", "3-5 hours", ["rebase-local"]),
        ],
    },
    {
        "order": 8,
        "slug": "systems-programming",
        "dir": "08-systems-programming",
        "title": "Linux Systems Programming",
        "description": "fork/exec, pipes, signals, threads, sockets, shared memory, and mmap.",
        "prerequisites": ["c", "debugging-gdb"],
        "challenges": [
            ("sys-file-descriptors", "easy", "File Descriptors", "30-60 minutes", ["fd", "dup"]),
            ("sys-pipes", "easy", "Pipes", "30-60 minutes", ["pipe"]),
            ("sys-process-controller", "medium", "Process Controller", "1-3 hours", ["fork", "exec", "wait"]),
            ("sys-tcp-client", "medium", "TCP Client", "1-2 hours", ["sockets"]),
            ("sys-threaded-server", "hard", "Multithreaded Server", "3-5 hours", ["pthreads", "mutex"]),
            ("sys-ipc", "hard", "IPC Investigation", "3-5 hours", ["shm", "mmap", "signals"]),
        ],
    },
    {
        "order": 9,
        "slug": "computer-architecture",
        "dir": "09-computer-architecture",
        "title": "Computer Architecture",
        "description": "ARM64 registers, endianness, assembly, stack, disassembly, and optimization.",
        "prerequisites": ["debugging-gdb"],
        "challenges": [
            ("arch-registers", "easy", "Registers", "30-60 minutes", ["arm64", "registers"]),
            ("arch-endianness", "easy", "Endianness", "20-45 minutes", ["endian"]),
            ("arch-c-to-asm", "medium", "C to Assembly", "1-2 hours", ["objdump", "gcc-S"]),
            ("arch-stack", "medium", "Stack Investigation", "1-3 hours", ["stack-frames"]),
            ("arch-disasm", "hard", "Disassembly Challenge", "2-4 hours", ["objdump", "readelf"]),
            ("arch-optimize", "hard", "Optimize the Program", "3-5 hours", ["perf-basics", "compiler-flags"]),
        ],
    },
    {
        "order": 10,
        "slug": "dsp-fundamentals",
        "dir": "10-dsp-fundamentals",
        "title": "DSP Fundamentals",
        "description": "Sinusoids, frequency measurement, sampling, aliasing, and a signal analyzer.",
        "prerequisites": ["python", "cpp"],
        "challenges": [
            ("dsp-sinusoid", "easy", "Generate a Sinusoid", "20-40 minutes", ["numpy", "signals"]),
            ("dsp-measure-freq", "easy", "Measure Frequency", "30-60 minutes", ["zero-crossings", "fft-intro"]),
            ("dsp-sampling", "medium", "Sampling", "1-2 hours", ["nyquist"]),
            ("dsp-aliasing", "medium", "Aliasing", "1-2 hours", ["aliasing"]),
            ("dsp-reconstruct", "hard", "Reconstruct the Signal", "2-4 hours", ["interpolation"]),
            ("dsp-analyzer", "hard", "Build a Signal Analyzer", "3-5 hours", ["python", "cpp-dsp"]),
        ],
    },
    {
        "order": 11,
        "slug": "fft",
        "dir": "11-fft-frequency-domain",
        "title": "FFT / Frequency Domain",
        "description": "FFT bins, spectral leakage, windowing, multi-tone analysis, spectrum analyzer.",
        "prerequisites": ["dsp-fundamentals"],
        "challenges": [
            ("fft-find-tone", "easy", "Find the Tone", "20-40 minutes", ["fft"]),
            ("fft-bin-challenge", "easy", "FFT Bin Challenge", "30-60 minutes", ["bins", "resolution"]),
            ("fft-leakage", "medium", "Spectral Leakage", "1-2 hours", ["leakage"]),
            ("fft-windowing", "medium", "Windowing", "1-2 hours", ["windows"]),
            ("fft-multitone", "hard", "Multi-tone Analysis", "2-4 hours", ["peaks"]),
            ("fft-spectrum-analyzer", "hard", "Build a Spectrum Analyzer", "3-5 hours", ["implement-fft"]),
        ],
    },
    {
        "order": 12,
        "slug": "dsp-filters",
        "dir": "12-dsp-filters",
        "title": "DSP Filters",
        "description": "FIR/IIR, convolution, mixing, frequency translation, decimation, interpolation.",
        "prerequisites": ["fft"],
        "challenges": [
            ("filt-lpf", "easy", "Low-pass Filter", "30-60 minutes", ["lpf"]),
            ("filt-hpf", "easy", "High-pass Filter", "30-60 minutes", ["hpf"]),
            ("filt-bpf", "medium", "Band-pass Challenge", "1-2 hours", ["bpf"]),
            ("filt-fir-design", "medium", "FIR Design", "1-3 hours", ["fir"]),
            ("filt-remove-interference", "hard", "Remove Interference", "2-4 hours", ["filtering"]),
            ("filt-dsp-pipeline", "hard", "Build a Complete DSP Pipeline", "3-5 hours",
             ["mix", "decimate", "filter"]),
        ],
    },
    {
        "order": 13,
        "slug": "gnu-radio",
        "dir": "13-gnu-radio",
        "title": "GNU Radio",
        "description": "Flowgraphs for generation, FFT, filtering, translation, and a complete receiver chain.",
        "prerequisites": ["dsp-filters"],
        "challenges": [
            ("gr-first-flowgraph", "easy", "First Flowgraph", "30-60 minutes", ["grc"]),
            ("gr-fft-flowgraph", "easy", "FFT Flowgraph", "30-60 minutes", ["fft-sink"]),
            ("gr-filtering", "medium", "Filtering Flowgraph", "1-2 hours", ["fir-filter"]),
            ("gr-freq-xlat", "medium", "Frequency Translation", "1-2 hours", ["xlating-fir"]),
            ("gr-recreate-python", "hard", "Recreate a Python DSP Algorithm", "3-5 hours", ["python-to-gr"]),
            ("gr-complete-rx", "hard", "Build a Complete Receiver Flowgraph", "3-6 hours",
             ["source", "filter", "xlat", "decimate", "viz"]),
        ],
    },
    {
        "order": 14,
        "slug": "iq-sdr",
        "dir": "14-iq-sdr-fundamentals",
        "title": "IQ / SDR Fundamentals",
        "description": "Complex baseband, wideband IQ analysis, bandwidth, and unknown captures — software-only.",
        "prerequisites": ["gnu-radio", "fft"],
        "challenges": [
            ("iq-identify", "easy", "Identify I/Q", "20-40 minutes", ["complex"]),
            ("iq-complex-analysis", "easy", "Complex Signal Analysis", "30-60 minutes", ["iq"]),
            ("iq-find-signal", "medium", "Find the Signal", "1-2 hours", ["wideband"]),
            ("iq-bandwidth", "medium", "Determine Bandwidth", "1-2 hours", ["bandwidth"]),
            ("iq-recover-baseband", "hard", "Recover a Baseband Signal", "2-4 hours", ["xlat", "filter"]),
            ("iq-unknown-capture", "hard", "Unknown IQ Capture", "3-5 hours",
             ["sample-rate", "location", "bw"]),
        ],
    },
    {
        "order": 15,
        "slug": "bpsk",
        "dir": "15-bpsk",
        "title": "BPSK",
        "description": "Identify and demodulate BPSK through noise, mapping, phase, and frequency offsets.",
        "prerequisites": ["iq-sdr"],
        "challenges": [
            ("bpsk-identify", "easy", "Identify BPSK", "20-40 minutes", ["constellation"]),
            ("bpsk-decode-clean", "easy", "Decode Clean BPSK", "30-60 minutes", ["demod"]),
            ("bpsk-noise", "medium", "BPSK with Noise", "1-2 hours", ["snr"]),
            ("bpsk-mapping", "medium", "BPSK with Unknown Symbol Mapping", "1-2 hours", ["mapping"]),
            ("bpsk-phase", "hard", "BPSK with Phase Offset", "2-4 hours", ["phase"]),
            ("bpsk-phase-freq", "hard", "BPSK with Phase + Frequency Offset", "3-5 hours",
             ["phase", "cfo"]),
        ],
    },
    {
        "order": 16,
        "slug": "qpsk",
        "dir": "16-qpsk",
        "title": "QPSK",
        "description": "QPSK constellations, Gray coding, noise, phase rotation, and frequency offset.",
        "prerequisites": ["bpsk"],
        "challenges": [
            ("qpsk-constellation", "easy", "Identify the Four Constellation Points", "20-40 minutes",
             ["qpsk"]),
            ("qpsk-decode-clean", "easy", "Decode Clean QPSK", "30-60 minutes", ["demod"]),
            ("qpsk-gray", "medium", "Gray Coding", "1-2 hours", ["gray"]),
            ("qpsk-noise", "medium", "QPSK with Noise", "1-2 hours", ["snr"]),
            ("qpsk-phase", "hard", "QPSK with Phase Rotation", "2-4 hours", ["phase"]),
            ("qpsk-freq", "hard", "QPSK with Unknown Frequency Offset", "3-5 hours", ["cfo"]),
        ],
    },
    {
        "order": 17,
        "slug": "pulse-shaping",
        "dir": "17-pulse-shaping",
        "title": "Pulse Shaping",
        "description": "Symbol rate, RRC, matched filtering, ISI, and eye diagrams.",
        "prerequisites": ["qpsk"],
        "challenges": [
            ("pulse-observe", "easy", "Observe Symbol Pulses", "20-40 minutes", ["symbols"]),
            ("pulse-compare", "easy", "Compare Pulse Shapes", "30-60 minutes", ["rect", "sinc"]),
            ("pulse-rc", "medium", "Raised Cosine", "1-2 hours", ["rc"]),
            ("pulse-rrc", "medium", "Root Raised Cosine", "1-2 hours", ["rrc"]),
            ("pulse-matched", "hard", "Matched Filter", "2-4 hours", ["matched-filter"]),
            ("pulse-isi", "hard", "Recover a Signal with ISI", "3-5 hours", ["isi", "eye"]),
        ],
    },
    {
        "order": 18,
        "slug": "synchronization",
        "dir": "18-synchronization",
        "title": "Synchronization",
        "description": "Phase/frequency correction, timing recovery, Costas, Gardner, Mueller & Müller.",
        "prerequisites": ["pulse-shaping"],
        "challenges": [
            ("sync-static-phase", "easy", "Static Phase Offset", "30-60 minutes", ["phase"]),
            ("sync-identify-freq", "easy", "Identify Frequency Offset", "30-60 minutes", ["cfo"]),
            ("sync-correct-phase", "medium", "Correct Phase", "1-2 hours", ["phase-recovery"]),
            ("sync-correct-freq", "medium", "Correct Frequency", "1-3 hours", ["freq-recovery"]),
            ("sync-timing", "hard", "Timing Offset", "2-4 hours", ["timing"]),
            ("sync-carrier-timing", "hard", "Carrier + Timing Synchronization", "3-6 hours",
             ["pll", "gardner"]),
        ],
    },
    {
        "order": 19,
        "slug": "complete-receivers",
        "dir": "19-complete-receivers",
        "title": "Complete Digital Receivers",
        "description": "End-to-end BPSK/QPSK receivers with impairments and unknown parameters.",
        "prerequisites": ["synchronization"],
        "challenges": [
            ("rx-bpsk", "easy", "BPSK Receiver", "1-2 hours", ["receiver"]),
            ("rx-qpsk", "easy", "QPSK Receiver", "1-2 hours", ["receiver"]),
            ("rx-noisy-qpsk", "medium", "Noisy QPSK Receiver", "2-3 hours", ["snr"]),
            ("rx-offset-qpsk", "medium", "Offset QPSK Receiver", "2-3 hours", ["offsets"]),
            ("rx-full", "hard", "Build the Full Receiver", "4-6 hours", ["pipeline"]),
            ("rx-unknown-params", "hard", "Unknown Receiver Parameters", "4-6 hours", ["estimation"]),
        ],
    },
    {
        "order": 20,
        "slug": "protocol-re",
        "dir": "20-protocol-re",
        "title": "Digital Protocol Reverse Engineering",
        "description": "Bits to bytes, headers, packet structure, CRC, and unknown protocol decoders.",
        "prerequisites": ["complete-receivers"],
        "challenges": [
            ("proto-bit-byte", "easy", "Bit to Byte", "20-40 minutes", ["framing"]),
            ("proto-header", "easy", "Identify the Header", "30-60 minutes", ["headers"]),
            ("proto-packet", "medium", "Packet Structure", "1-2 hours", ["packets"]),
            ("proto-crc", "medium", "CRC", "1-3 hours", ["crc"]),
            ("proto-unknown", "hard", "Unknown Protocol", "3-5 hours", ["re"]),
            ("proto-decoder", "hard", "Build a Decoder", "3-6 hours", ["tooling"]),
        ],
    },
    {
        "order": 21,
        "slug": "sdr-security-ctf",
        "dir": "21-sdr-security-ctf",
        "title": "SDR Security CTF",
        "description": "RF/security CTF using software-simulated IQ captures — find, demod, and reverse.",
        "prerequisites": ["protocol-re"],
        "challenges": [
            ("ctf-hidden-tx", "easy", "Find the Hidden Transmission", "30-60 minutes", ["spectrum"]),
            ("ctf-identify-mod", "easy", "Identify the Modulation", "30-60 minutes", ["modulation"]),
            ("ctf-recover-bits", "medium", "Recover the Bits", "1-3 hours", ["demod"]),
            ("ctf-correct-impair", "medium", "Correct the Impairments", "2-3 hours", ["sync"]),
            ("ctf-re-protocol", "hard", "Reverse Engineer the Protocol", "3-5 hours", ["protocol"]),
            ("ctf-complete-capture", "hard", "Complete RF Capture", "4-6 hours", ["integrate"]),
        ],
    },
    {
        "order": 99,
        "slug": "capstone-blackout",
        "dir": "99-capstone-blackout",
        "title": "Final Capstone — Blackout",
        "description": "Unknown IQ capture combining the full curriculum into one ≤6h focused session.",
        "prerequisites": ["sdr-security-ctf"],
        "challenges": [
            ("capstone-blackout", "hard", "Blackout", "4-6 hours",
             ["linux", "python", "cpp", "gdb", "cmake", "dsp", "gnuradio", "iq", "sync", "protocol"]),
        ],
    },
]


DIFF_HINTS = {
    "easy": [
        "Look carefully at the files provided in your workspace.",
        "Read the challenge README and list what tools you already know.",
        "Try the simplest command or plot that reveals structure before writing code.",
    ],
    "medium": [
        "Inventory every file and measurement you can make without changing anything.",
        "Write down hypotheses, then test the cheapest one first.",
        "Compare against a known-good example from a prior module if available.",
        "Automate once you can do the steps manually once.",
    ],
    "hard": [
        "Break the problem into observe → model → implement → verify stages.",
        "Validate intermediate outputs (spectrum, constellation, packets) before chasing the flag.",
        "If stuck, re-derive the signal/processing chain on paper with known parameters.",
        "Add logging or GDB/print checks at each pipeline stage.",
        "When parameters are unknown, estimate them from the data rather than guessing blindly.",
    ],
}


def yaml_escape(s: str) -> str:
    if any(c in s for c in [":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", ">", "'", '"', "%", "@", "`"]):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def write_module(mod: dict, fully_authored_ids: set[str]) -> None:
    mdir = ROOT / mod["dir"]
    mdir.mkdir(parents=True, exist_ok=True)
    (mdir / "challenges").mkdir(exist_ok=True)

    challenge_ids = [c[0] for c in mod["challenges"]]
    module_yaml = f"""id: {mod['slug']}
slug: {mod['slug']}
title: {yaml_escape(mod['title'])}
order: {mod['order']}
description: |
  {mod['description']}
prerequisites:
"""
    if mod["prerequisites"]:
        for p in mod["prerequisites"]:
            module_yaml += f"  - {p}\n"
    else:
        module_yaml += "  []\n"
    module_yaml += "challenges:\n"
    for cid in challenge_ids:
        module_yaml += f"  - {cid}\n"

    (mdir / "module.yaml").write_text(module_yaml, encoding="utf-8")

    for cid, difficulty, title, etime, objectives in mod["challenges"]:
        if cid in fully_authored_ids:
            continue
        cdir = mdir / "challenges" / cid
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "files").mkdir(exist_ok=True)
        (cdir / "solution").mkdir(exist_ok=True)
        readme = cdir / "files" / "README_STARTER.txt"
        if not readme.exists():
            readme.write_text(
                f"Starter workspace for {cid}. Full challenge content TBD — scaffold only.\n",
                encoding="utf-8",
            )

        # Soft prerequisite: previous challenge in module when present
        idx = challenge_ids.index(cid)
        prereqs = []
        if idx > 0:
            prereqs.append(challenge_ids[idx - 1])
        for p in mod["prerequisites"]:
            prereqs.append(f"module:{p}")

        hints = DIFF_HINTS[difficulty]
        flag = f"flag{{{cid.replace('-', '_')}_pending}}"

        ch = f"""id: {cid}
module: {mod['slug']}
title: {yaml_escape(title)}
difficulty: {difficulty}
estimated_time: "{etime}"

prerequisites:
"""
        for p in prereqs:
            ch += f"  - {p}\n"
        ch += "\nobjectives:\n"
        for o in objectives:
            ch += f"  - {o}\n"
        ch += f"""
mastery_evidence:
  - understand
  - observe
  - apply

description: |
  **Scaffold challenge** — full narrative, datasets, and validators will be authored
  in a later content pass. This stub reserves the ID, difficulty, and learning goals
  from the master curriculum specification.

  Goal sketch: {title}.

environment:
  type: workspace
  workspace_subdir: {cid}
  notes: Software-only; no external hardware or network required.

files:
  - README_STARTER.txt

expected_tools:
  - bash
  - python3

flags:
  value: "{flag}"
  validation: exact

hints:
"""
        for i, h in enumerate(hints, 1):
            ch += f"  - level: {i}\n    text: |\n      {h}\n"
        ch += f"""
solution: |
  Solution pending full challenge authoring for `{cid}`.

explanation: |
  Explanation pending full challenge authoring for `{cid}`.

extension:
  title: "Go further"
  description: |
    Optional extension will be defined when this challenge is fully authored.

performance_notes: |
  Keep datasets and runtime suitable for Raspberry Pi (avoid multi-GB IQ unless decimated).

optional_hardware: []
"""
        (cdir / "challenge.yaml").write_text(ch, encoding="utf-8")


def main() -> None:
    # Module 0 is fully authored separately; skip overwriting those challenge.yaml files
    authored = {
        "orient-find-flag",
        "orient-permissions",
        "orient-process-hunt",
        "orient-environment",
        "orient-broken-service",
        "orient-system-investigation",
    }
    for mod in MODULES:
        write_module(mod, authored if mod["slug"] == "orientation" else set())
    print(f"Generated {len(MODULES)} modules under {ROOT}")


if __name__ == "__main__":
    main()
