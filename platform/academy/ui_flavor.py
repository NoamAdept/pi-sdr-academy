"""Creative display titles + generated challenge thumbnails."""

from __future__ import annotations

import hashlib

TITLES: dict[str, str] = {
    "orient-find-flag": "Needle in the Labyrinth",
    "orient-permissions": "The Locked Drawer",
    "orient-process-hunt": "Ghost in the Process List",
    "orient-environment": "Whispered Variables",
    "orient-broken-service": "The Silent Port",
    "orient-system-investigation": "Autopsy of a Pi",
    "cli-pipeline": "Pipe Dream",
    "cli-text-extraction": "Frequencies in the Fog",
    "cli-log-detective": "Receiver Log Noir",
    "cli-multistage-pipeline": "Locked-Signal Census",
    "cli-shell-automation": "Night Watch Inventory",
    "cli-build-tool": "Make It Speak C",
    "py-control-flow": "Strength Classifier",
    "py-file-parser": "Config Crypt",
    "py-binary-decoder": "Sensor Bones",
    "py-protocol-parser": "Noisy Frame Tamer",
    "py-socket-client": "Knock on Localhost",
    "py-auto-investigator": "The Autopilot Probe",
    "c-compile-it": "First Blood Compile",
    "c-pointer-basics": "Follow the Arrow",
    "c-debug-crash": "Array Overboard",
    "c-memory-layout": "Bytes Under Glass",
    "c-binary-parser": "Length-Prefixed Prey",
    "c-re-datastruct": "The Missing Link",
    "gdb-first-breakpoint": "Stop Right There",
    "gdb-find-variable": "The Moving Target",
    "gdb-follow-stack": "Down the Call Well",
    "gdb-inspect-memory": "Peek Behind the Bytes",
    "gdb-logic-bug": "Wrong Answer, Right Place",
    "gdb-segfault": "The Crash Site",
    "cpp-first-class": "Class in Session",
    "cpp-raii": "Own the File",
    "cpp-smart-ptr": "The Ownership Tree",
    "cpp-stl": "Sample Census",
    "cpp-mini-lib": "Library of Echoes",
    "cpp-debug-app": "Receiver on the Table",
    "cmake-first": "CMake Dawn",
    "cmake-targets": "Two Fires, One Build",
    "cmake-static-lib": "Stone Library",
    "cmake-multidir": "Across the Folders",
    "cmake-dep-debug": "Broken Link, Fixed Chain",
    "cmake-ctest": "Prove It Runs",
    "git-first-repo": "First Commit Stone",
    "git-branch-merge": "Two Paths, One History",
    "git-commit-invest": "Who Touched the Wire?",
    "git-debug-history": "The Regression Ghost",
    "git-recover-deleted": "Undelete the Signal",
    "git-repair-history": "Revert the Wound",
    "sys-pipes": "Parent, Child, Pipe",
    "sys-ipc": "Shared Memory Handshake",
    "sys-file-descriptors": "Copy Through the FD",
    "sys-process-controller": "Puppet the Child",
    "sys-tcp-client": "Local Wire Tap",
    "sys-threaded-server": "Two Clients, One Door",
    "pt-py-process": "Send the Child Out",
    "pt-py-threads": "Many Hands, One Counter",
    "pt-cpp-process": "Fork in the Wire",
    "pt-cpp-threads": "std::thread Assembly Line",
    "arch-registers": "Name the Registers",
    "arch-endianness": "Which Byte Walks First?",
    "arch-stack": "Up or Down the Stack",
    "arch-c-to-asm": "C’s Shadow in Assembly",
    "arch-disasm": "Read the Machine’s Hand",
    "arch-optimize": "Fast vs Faithful",
    "dsp-sinusoid": "Draw the Sine",
    "dsp-sampling": "The Nyquist Line",
    "dsp-aliasing": "The Impostor Tone",
    "dsp-measure-freq": "Count the Cycles",
    "dsp-reconstruct": "Fill the Missing Samples",
    "dsp-analyzer": "Pocket Spectrum",
    "fft-find-tone": "One Peak in the Dark",
    "fft-bin-challenge": "Which Bin Holds the Note?",
    "fft-multitone": "A Chord of Peaks",
    "fft-leakage": "Energy That Spills",
    "fft-windowing": "Close the Curtains",
    "fft-spectrum-analyzer": "Full Spectrum Watch",
    "filt-lpf": "Let the Lows Through",
    "filt-hpf": "Cut the Rumble",
    "filt-bpf": "A Window in Frequency",
    "filt-fir-design": "Tap the Impulse",
    "filt-remove-interference": "Kill the Whistle",
    "filt-dsp-pipeline": "The Filter Chain",
    "gr-first-flowgraph": "First Graph of Radio",
    "gr-fft-flowgraph": "FFT on the Canvas",
    "gr-filtering": "Blocks That Sift",
    "gr-freq-xlat": "Slide the Spectrum",
    "gr-recreate-python": "Redraw It in Python",
    "gr-complete-rx": "A Receiver in Miniature",
    "iq-identify": "Name That Capture",
    "iq-find-signal": "Blip in the Waterfall",
    "iq-bandwidth": "How Wide Is the Voice?",
    "iq-recover-baseband": "Bring It Home to DC",
    "iq-complex-analysis": "I and Q, Face to Face",
    "iq-unknown-capture": "File With No Name",
    "bpsk-identify": "Two Stars, One Axis",
    "bpsk-mapping": "Bits on the Line",
    "bpsk-decode-clean": "Clean BPSK, Clear Text",
    "bpsk-noise": "BPSK in the Static",
    "bpsk-phase": "Spin It Until It Locks",
    "bpsk-phase-freq": "Phase and Drift",
    "qpsk-constellation": "Four Corners of QPSK",
    "qpsk-gray": "Gray Code Compass",
    "qpsk-decode-clean": "Four Points, No Fog",
    "qpsk-noise": "QPSK in the Rain",
    "qpsk-phase": "Rotate the Diamond",
    "qpsk-freq": "The Sliding Diamond",
    "pulse-observe": "Watch the Symbols Breathe",
    "pulse-compare": "Which Pulse Sings Cleaner?",
    "pulse-rc": "Nyquist’s Zero Crossings",
    "pulse-rrc": "Guess the Roll-Off",
    "pulse-isi": "Stop the Symbol Bleed",
    "pulse-matched": "The Filter That Fits",
    "sync-static-phase": "A Frozen Angle",
    "sync-identify-freq": "How Fast Does It Drift?",
    "sync-correct-phase": "Unknown Twist",
    "sync-correct-freq": "Nail the Offset",
    "sync-timing": "Hit the Symbol Center",
    "sync-carrier-timing": "Lock Both Loops",
    "rx-bpsk": "Stand Up a BPSK RX",
    "rx-qpsk": "Stand Up a QPSK RX",
    "rx-noisy-qpsk": "QPSK Through the Storm",
    "rx-offset-qpsk": "Off-Center QPSK",
    "rx-unknown-params": "Receiver, No Cheat Sheet",
    "rx-full": "The Whole Chain",
    "proto-header": "Where Does the Packet Start?",
    "proto-bit-byte": "Bits Into Bytes",
    "proto-packet": "Map the Frame",
    "proto-crc": "The Checksum Fingerprint",
    "proto-decoder": "A Decoder You Can Reuse",
    "proto-unknown": "Protocol From Thin Air",
    "ctf-identify-mod": "Name the Modulation",
    "ctf-recover-bits": "Pull the Bitstream",
    "ctf-correct-impair": "Undo the Damage",
    "ctf-hidden-tx": "The Hidden Transmitter",
    "ctf-re-protocol": "Break the Air Protocol",
    "ctf-complete-capture": "Finish the Capture",
    "pyq-oop-classes": "Meters as Objects",
    "pyq-collections": "Event Ledger",
    "pyq-modules-packages": "The Broken Package",
    "pyq-context-exceptions": "Guard the Session",
    "pyq-modern-python": "Typed Packet Router",
    "pyq-bits-serialize": "Binary Radio Record",
    "cppq-namespaces-const": "Names and Armor",
    "cppq-strings-files": "Config That Lasts",
    "cppq-errors-optional": "Failure, Named",
    "cppq-templates": "Generic Decoder Buffer",
    "cppq-modern-cpp": "Modern Channel Scanner",
    "cppq-lowlevel-concurrency": "ISR Packet Rescue",
    "grq-cpp-blocks": "Blocks and Handles",
    "grq-vector-dataflow": "Items Down the Vector",
    "grq-flowgraph-connect": "Wire the Ports",
    "grq-tags-messages": "Tags Are Not Messages",
    "grq-signal-chain": "Translating Chain",
    "grq-complete-topblock": "Qualification Top Block",
    "capstone-blackout": "Blackout",
}


def display_title(challenge_id: str, fallback: str = "") -> str:
    return TITLES.get(challenge_id, fallback or challenge_id)


def _palette(challenge_id: str) -> tuple[str, str, str, str]:
    digest = hashlib.sha256(challenge_id.encode()).digest()
    hues = [digest[i] for i in range(6)]
    a = f"hsl({hues[0] * 360 // 255}, 70%, 48%)"
    b = f"hsl({hues[1] * 360 // 255}, 65%, 38%)"
    c = f"hsl({(hues[2] * 360 // 255 + 40) % 360}, 80%, 58%)"
    ink = "#c8ff00" if digest[3] % 2 == 0 else "#4ecdc4"
    return a, b, c, ink


def challenge_thumb_svg(challenge_id: str) -> str:
    """Tiny unique ‘photo’ — geometric signal art, unique per challenge id."""
    digest = hashlib.sha256(challenge_id.encode()).digest()
    a, b, c, ink = _palette(challenge_id)
    gid = digest[:4].hex()
    kind = digest[4] % 6
    extras: list[str] = []
    # Soft orbs so each thumb reads like a tiny photo, not a glyph.
    extras.append(
        f'<ellipse cx="{40 + digest[5] % 80}" cy="{28 + digest[6] % 40}" '
        f'rx="{28 + digest[7] % 24}" ry="{18 + digest[8] % 16}" fill="{c}" opacity="0.35"/>'
    )
    extras.append(
        f'<ellipse cx="{90 + digest[9] % 50}" cy="{70 + digest[10] % 30}" '
        f'rx="{20 + digest[11] % 20}" ry="{14 + digest[12] % 14}" fill="#050705" opacity="0.25"/>'
    )
    if kind == 0:
        extras.append(
            f'<path d="M8 {40 + digest[13] % 30} C 28 20, 48 108, 88 {30 + digest[14] % 40} '
            f'S 140 20, 152 64" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>'
        )
    elif kind == 1:
        for i in range(8):
            h = 18 + (digest[5 + i] % 70)
            extras.append(
                f'<rect x="{14 + i * 17}" y="{120 - h}" width="12" height="{h}" rx="2" '
                f'fill="{ink}" opacity="{0.35 + (i % 3) * 0.2}"/>'
            )
    elif kind == 2:
        extras.append(f'<circle cx="58" cy="58" r="22" fill="none" stroke="{ink}" stroke-width="3"/>')
        extras.append(f'<circle cx="102" cy="70" r="16" fill="{c}" opacity="0.85"/>')
        extras.append(f'<circle cx="80" cy="86" r="8" fill="{ink}"/>')
    elif kind == 3:
        extras.append(f'<polygon points="80,18 132,104 28,104" fill="none" stroke="{ink}" stroke-width="3"/>')
        extras.append(f'<circle cx="80" cy="72" r="10" fill="{c}"/>')
    elif kind == 4:
        extras.append(f'<path d="M24 96 L80 24 L136 96" fill="none" stroke="{ink}" stroke-width="4"/>')
        extras.append(f'<rect x="56" y="72" width="48" height="28" rx="4" fill="{c}" opacity="0.8"/>')
    else:
        extras.append(
            f'<path d="M12 90 Q 40 {20 + digest[15] % 40}, 80 70 T 148 {40 + digest[16] % 40}" '
            f'fill="none" stroke="{ink}" stroke-width="3.5" stroke-linecap="round"/>'
        )
        extras.append(f'<rect x="18" y="18" width="28" height="18" rx="3" fill="{ink}" opacity="0.55"/>')
    grain = []
    for i in range(18):
        x = 8 + (digest[(i + 3) % 32] * (i + 7)) % 144
        y = 8 + (digest[(i + 11) % 32] * (i + 3)) % 104
        grain.append(f'<circle cx="{x}" cy="{y}" r="1.1" fill="#f2f7f2" opacity="0.18"/>')
    glyph = "".join(part[0].upper() for part in challenge_id.split("-")[:2])[:2]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 120" width="160" height="120">
  <defs>
    <linearGradient id="g{gid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{a}"/>
      <stop offset="1" stop-color="{b}"/>
    </linearGradient>
  </defs>
  <rect width="160" height="120" fill="url(#g{gid})"/>
  <rect x="6" y="6" width="148" height="108" rx="14" fill="#050705" opacity="0.28"/>
  {''.join(extras)}
  {''.join(grain)}
  <text x="14" y="108" font-family="ui-monospace, Menlo, monospace" font-size="14" fill="#f2f7f2" opacity="0.9">{glyph}</text>
</svg>
'''
