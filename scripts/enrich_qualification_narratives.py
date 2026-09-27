#!/usr/bin/env python3
"""Enrich qualification challenges with academy-style SDR narratives and READMEs."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

ROOT_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_REPO / "vendor"))
import yaml

ROOT = Path("/workspace/curriculum/modules")

NARRATIVE: dict[str, dict[str, str]] = {
    "qual-py-overview": {
        "desc": (
            "Open OVERVIEW.txt — the map of this Python qualification path — and write "
            "the exact track id `python-qualification` into answer.txt on one line. "
            "This mirrors the syllabus overview notebook before hands-on modules begin."
        ),
        "h1": "Read OVERVIEW.txt first; it names the track.",
        "h2": "answer.txt must contain exactly one line with the track id.",
        "h3": "The exact spelling is python-qualification (hyphenated).",
        "expl": (
            "Qualification overviews orient you before coding. Naming the track id "
            "locks progress to the right side path in the dojo."
        ),
        "goal": "Write the track id python-qualification into answer.txt after reading OVERVIEW.txt.",
    },
    "qual-py-modules": {
        "desc": (
            "The radio rack needs a shared math helper. Complete wavelength_m(mhz) in "
            "radio_math.py so it returns free-space wavelength in meters using c=299792458 "
            "and frequency in Hz (mhz * 1e6). Keep the math import — modules package reusable lab code."
        ),
        "h1": "Free-space wavelength is c / f with c = 299792458 m/s.",
        "h2": "Convert MHz to Hz with mhz * 1e6 before dividing.",
        "h3": "return 299792458 / (mhz * 1e6)",
        "expl": (
            "Modules and imports keep radio math in one place so every script can "
            "reuse the same wavelength helper without copy-paste."
        ),
        "goal": "Implement wavelength_m(mhz) returning meters for free-space wavelength.",
    },
    "qual-py-types": {
        "desc": (
            "Bench notes arrive as mixed ints, floats, and digit strings. Complete "
            "coerce_samples so every value becomes a float in a new list, preserving order. "
            "Dynamic typing means you coerce at DSP edges instead of declaring types up front."
        ),
        "h1": "Call float(x) on each value.",
        "h2": "A list comprehension keeps order and builds a new list.",
        "h3": "return [float(v) for v in values]",
        "expl": (
            "Python is dynamically typed. Coercing at the boundary of a signal path "
            "keeps later DSP steps from mixing str and float by accident."
        ),
        "goal": "Convert mixed sample values to list[float] with coerce_samples.",
    },
    "qual-py-oop": {
        "desc": (
            "Model a small bench instrument: SignalMeter stores power readings in dB. "
            "Implement add to record a reading and average to return the mean, or 0.0 when "
            "empty. Classes turn instruments into objects you can reuse across lab scripts."
        ),
        "h1": "append each power_db into the internal list.",
        "h2": "average is sum(readings) / len(readings).",
        "h3": "If the list is empty, return 0.0 instead of dividing.",
        "expl": (
            "Object-oriented design models lab gear as objects with state (readings) "
            "and behavior (add, average)."
        ),
        "goal": "Implement SignalMeter.add and SignalMeter.average (0.0 if empty).",
    },
    "qual-py-immutable": {
        "desc": (
            "IQ sample pairs should not be mutated after capture. Complete iq_pair so it "
            "returns an immutable (i, q) tuple — not a list. In Python, immutability is a "
            "property of the object type, similar in spirit to C++ const data."
        ),
        "h1": "Return a tuple, not a list.",
        "h2": "Pack both components: (i, q).",
        "h3": "return (i, q)",
        "expl": (
            "Tuples protect captured samples from accidental in-place edits that lists allow."
        ),
        "goal": "Return an immutable (i, q) tuple from iq_pair.",
    },
    "qual-py-refs": {
        "desc": (
            "Python names reference objects. Complete share_buffer so it returns the same "
            "list object (an alias), and mutate_last so it changes the last element in place. "
            "Understanding aliases prevents surprise mutations in shared sample buffers."
        ),
        "h1": "share_buffer should return buf itself, not a copy.",
        "h2": "mutate_last assigns buf[-1] = value.",
        "h3": "Do not slice or list() — that would copy.",
        "expl": (
            "Multiple names can point at one list. In-place edits show up everywhere "
            "that alias is used — useful for buffers, dangerous if unexpected."
        ),
        "goal": "Alias the buffer with share_buffer; mutate the last sample in place.",
    },
    "qual-py-modern": {
        "desc": (
            "Operator logs need clear tune lines. Complete format_tune so it returns "
            "exactly `tune LABEL @ MHz` with the frequency to three decimal places "
            "(for example tune NFM @ 146.520 MHz). Modern f-strings keep lab logs readable."
        ),
        "h1": "Use an f-string for the whole line.",
        "h2": "Format MHz with :.3f",
        "h3": "Exact text: f'tune {label} @ {mhz:.3f} MHz'",
        "expl": (
            "F-strings and precise formatting make radio logs easy to scan during a session."
        ),
        "goal": "Return a tune log line with label and MHz to three decimals.",
    },
    "qual-py-collections": {
        "desc": (
            "From a list of amplitude samples, return the indices where the sample is "
            "strictly above a threshold. Comprehensions with enumerate are the Pythonic "
            "way to filter a stream without a verbose for-loop."
        ),
        "h1": "enumerate(samples) gives index and value together.",
        "h2": "Keep indices where sample > thresh.",
        "h3": "[i for i, s in enumerate(samples) if s > thresh]",
        "expl": (
            "Comprehensions filter and transform collections in one expression — "
            "ideal for peak picking on short captures."
        ),
        "goal": "Return indices of samples strictly above the threshold.",
    },
    "qual-py-context": {
        "desc": (
            "Capture files must always close. Implement read_capture with a with-open "
            "context manager and return the file text stripped of surrounding whitespace. "
            "Context managers are Python's RAII for files and other resources."
        ),
        "h1": "Use `with open(path) as f:` so the file always closes.",
        "h2": "Read the whole file, then strip().",
        "h3": "The word `with` must appear in capture.py for the check to pass.",
        "expl": (
            "with-open guarantees cleanup even when an error interrupts the read — "
            "the same idea as RAII in C++."
        ),
        "goal": "Read a capture file with with-open and return stripped text.",
    },
    "qual-py-exceptions": {
        "desc": (
            "Flags in this academy look like flag{...}. Complete parse_flag to strip "
            "whitespace, accept a valid flag, and raise ValueError for anything else. "
            "Exceptions beat silent None returns when operator input is wrong."
        ),
        "h1": "Strip whitespace first.",
        "h2": "Valid text starts with flag{ and ends with }.",
        "h3": "raise ValueError when the shape is wrong.",
        "expl": (
            "Raising ValueError makes bad input obvious at the call site instead of "
            "passing a bogus flag downstream."
        ),
        "goal": "Return a valid flag{...} string or raise ValueError.",
    },
    "qual-py-packaging": {
        "desc": (
            "A tiny labkit package already sits beside your loader. Complete load_version "
            "so it imports labkit and returns its version string. Packages and "
            "__init__.py turn a folder into an importable toolkit for the Pi lab."
        ),
        "h1": "import labkit (the folder is already present).",
        "h2": "Read labkit.version after importing.",
        "h3": "return labkit.version",
        "expl": (
            "Package layouts let you share helpers across challenges and scripts "
            "without dumping everything in one file."
        ),
        "goal": "Import labkit and return its version string.",
    },
    "qual-py-bits": {
        "desc": (
            "Beacon headers on the wire are bytes. Complete pack_header so it packs two "
            "unsigned 16-bit integers as big-endian using struct — seq then code — into "
            "exactly four bytes. Endianness matters for SDR and network formats."
        ),
        "h1": "Use struct.pack with a format string.",
        "h2": "Big-endian unsigned shorts use >HH.",
        "h3": "struct.pack('>HH', seq, code)",
        "expl": (
            "struct packs Python ints into exact on-wire byte layouts for beacons and protocols."
        ),
        "goal": "Pack two big-endian uint16 values into four bytes.",
    },
    "qual-py-dataclass": {
        "desc": (
            "Frame already uses @dataclass with freq_mhz and note. Complete to_json so it "
            "serializes a Frame through asdict and json.dumps. Dataclasses plus JSON are "
            "how lab logs move between scripts without hand-written dicts."
        ),
        "h1": "asdict(frame) builds a plain dict from the dataclass.",
        "h2": "json.dumps turns that dict into a string.",
        "h3": "return json.dumps(asdict(frame))",
        "expl": (
            "Dataclasses hold structured lab records; asdict + json makes them portable."
        ),
        "goal": "Serialize a Frame dataclass to a JSON string via asdict.",
    },
    "qual-py-decorators": {
        "desc": (
            "Write a counted decorator that wraps a function, exposes .calls starting at 0, "
            "and increments on every call while returning the original result. Decorators "
            "are the clean way to add timing or counters around DSP helpers."
        ),
        "h1": "Define an inner wrapper that calls fn(*args, **kwargs).",
        "h2": "Keep a calls counter on the wrapper, starting at 0.",
        "h3": "Increment calls before or after invoking fn; return fn's result.",
        "expl": (
            "Decorators wrap cross-cutting behavior (counts, timing) without editing "
            "every call site."
        ),
        "goal": "Implement counted(fn) with a .calls counter on the wrapper.",
    },
    "qual-py-typing": {
        "desc": (
            "Complete apply_gain so each sample is multiplied by gain into a new list. "
            "Type hints on the signature document the contract for static checkers even "
            "though Python still runs dynamically."
        ),
        "h1": "Build a new list; do not mutate the input in place.",
        "h2": "Multiply each sample by gain.",
        "h3": "return [s * gain for s in samples]",
        "expl": (
            "Type hints document DSP contracts for teammates and tools like mypy "
            "without changing runtime behavior."
        ),
        "goal": "Return a new list of samples scaled by gain.",
    },
    "qual-cpp-overview": {
        "desc": (
            "Read OVERVIEW.txt for the C++ qualification map and write the track id "
            "`cpp-qualification` into answer.txt on one line. Overview first — then "
            "namespaces through ISR-style flags in the challenges that follow."
        ),
        "h1": "Read OVERVIEW.txt; it names the track.",
        "h2": "One line in answer.txt with the track id.",
        "h3": "Exact spelling: cpp-qualification",
        "expl": (
            "The overview challenge mirrors the syllabus notebook and unlocks the path id."
        ),
        "goal": "Write cpp-qualification into answer.txt after reading OVERVIEW.txt.",
    },
    "qual-cpp-namespaces": {
        "desc": (
            "RadioMath already provides add inside a namespace. Finish sub so it returns "
            "a - b, and keep the program printing sum= and diff= via RadioMath::. "
            "Namespaces keep large radio codebases from colliding on short names."
        ),
        "h1": "Inside RadioMath::sub, return a - b.",
        "h2": "Do not remove the RadioMath namespace wrapper.",
        "h3": "main already prints with RadioMath::add and RadioMath::sub.",
        "expl": (
            "Scope resolution (RadioMath::) reaches names inside a namespace without "
            "polluting the global scope."
        ),
        "goal": "Implement RadioMath::sub and print sum and diff from main.",
    },
    "qual-cpp-data": {
        "desc": (
            "Operator notes live in tune.txt. Read the first line with getline and print "
            "tune=<line> (for example tune=146.52). Strings and fstream are the everyday "
            "tools for lab configuration files on the Pi."
        ),
        "h1": "tune.txt is already in the workspace.",
        "h2": "std::getline(in, line) reads the first line.",
        "h3": "Print exactly: tune= followed by the line contents.",
        "expl": (
            "ifstream + getline load text configs the same way operators keep tune cards."
        ),
        "goal": "Read the first line of tune.txt and print tune=<line>.",
    },
    "qual-cpp-oop": {
        "desc": (
            "Tone stores a frequency in Hz behind a private field. Finish freq() so it "
            "returns hz_ and main prints freq=440. Classes encapsulate synthesizer state "
            "the way real tone blocks hide their internals."
        ),
        "h1": "freq() should return the private hz_ member.",
        "h2": "Keep the method const — it only reads state.",
        "h3": "return hz_;",
        "expl": (
            "Encapsulation keeps signal state private and exposes a small public API."
        ),
        "goal": "Return hz_ from Tone::freq so main prints freq=440.",
    },
    "qual-cpp-const": {
        "desc": (
            "scale_const takes a const int& sample and a gain. Return sample * gain "
            "without assigning through the const reference, and print scaled=6. const "
            "documents read-only paths through a DSP stage."
        ),
        "h1": "Return sample * gain.",
        "h2": "Do not write to sample — it is const.",
        "h3": "Keep the const int& parameter type.",
        "expl": (
            "const references pass large values cheaply while promising not to mutate them."
        ),
        "goal": "Multiply a const sample by gain and print scaled=6.",
    },
    "qual-cpp-pointers": {
        "desc": (
            "sample starts at 0 and p points at it. Write 42 through the pointer (*p) so "
            "main prints value=42. Pointers address live sample memory — powerful and "
            "easy to misuse, which is why this qualification drills them early."
        ),
        "h1": "p already holds &sample.",
        "h2": "Assign through the pointer: *p = 42;",
        "h3": "Printing sample afterward should show 42.",
        "expl": (
            "A pointer holds an address; dereferencing it reads or writes the live object."
        ),
        "goal": "Set the live sample to 42 through a pointer and print value=42.",
    },
    "qual-cpp-modern": {
        "desc": (
            "Sum a vector of gains with a range-based for loop and print sum=6. Modern "
            "C++ prefers range-for over index loops when you only need each element."
        ),
        "h1": "for (int g : gains) walks every element.",
        "h2": "Add each g into sum.",
        "h3": "Keep the final print of sum=.",
        "expl": (
            "Range-for is clearer and less error-prone than manual indexing for simple scans."
        ),
        "goal": "Sum gains with range-for and print sum=6.",
    },
    "qual-cpp-stl": {
        "desc": (
            "Use std::max_element on a vector of samples and print peak=<value>. The STL "
            "ships containers and algorithms so you do not hand-roll every search on a "
            "spectrum snapshot."
        ),
        "h1": "max_element returns an iterator to the largest element.",
        "h2": "Dereference the iterator with *it to get the value.",
        "h3": "Keep #include <algorithm>.",
        "expl": (
            "STL algorithms express intent (maximum) without writing the comparison loop."
        ),
        "goal": "Find the peak with std::max_element and print peak=9.",
    },
    "qual-cpp-raii": {
        "desc": (
            "Own an int with std::unique_ptr (value 7) and print owned=7. RAII and smart "
            "pointers free resources when the owner leaves scope — the C++ answer to "
            "manual new/delete bugs in long-running radio processes."
        ),
        "h1": "std::make_unique<int>(7) builds an owning pointer.",
        "h2": "Dereference with *p to read the value.",
        "h3": "unique_ptr must appear in main.cpp.",
        "expl": (
            "When unique_ptr goes out of scope it deletes the object — no leak, no double-free."
        ),
        "goal": "Own int(7) with unique_ptr and print owned=7.",
    },
    "qual-cpp-errors": {
        "desc": (
            "apply_gain throws std::invalid_argument on negative gain. Keep the throw, "
            "print ok=8 for a good call, then catch the bad call and print caught. "
            "Exceptions make unsafe operator input visible instead of returning magic codes."
        ),
        "h1": "The throw on gain < 0 is already written — keep it.",
        "h2": "Good path should print ok= followed by the product.",
        "h3": "catch (const std::invalid_argument&) should print caught.",
        "expl": "Throwing on bad gain stops silent corruption of the signal path.",
        "goal": "Throw on negative gain; print ok=8 then caught.",
    },
    "qual-cpp-cmake": {
        "desc": (
            "Pretend your CMake target is named beacon_rx. Print target=beacon_rx from "
            "main. Build systems name radio binaries; this challenge only checks you can "
            "treat that name as a first-class constant in code."
        ),
        "h1": "Store the string beacon_rx in a std::string.",
        "h2": "Print target= then the string.",
        "h3": "Spelling must be exactly beacon_rx.",
        "expl": (
            "CMake targets name the artifacts operators run — keep those names consistent."
        ),
        "goal": "Print target=beacon_rx as your CMake-style binary name.",
    },
    "qual-cpp-packages": {
        "desc": (
            "A local labkit.hpp sits beside main.cpp. Include it with quotes and print "
            "ver= from labkit_version(). Vendored headers are how small C++ packages "
            "ship helpers without a full system install."
        ),
        "h1": '#include "labkit.hpp"',
        "h2": "Call labkit_version().",
        "h3": "Print ver= followed by the returned int.",
        "expl": (
            "Quoted includes pull headers from the project tree — the start of real packaging."
        ),
        "goal": "Include labkit.hpp and print ver=1.",
    },
    "qual-cpp-bits": {
        "desc": (
            "Split uint16 0xABCD into big-endian high and low bytes and print hex=abcd. "
            "Shifts and masks build beacon headers and protocol fields the same way "
            "embedded radio firmware does."
        ),
        "h1": "High byte is (id >> 8) & 0xFF.",
        "h2": "Low byte is id & 0xFF.",
        "h3": "Print both nibbles in hex after hex=.",
        "expl": (
            "Bit ops let you lay out multi-byte IDs without depending on host endianness."
        ),
        "goal": "Pack 0xABCD as big-endian bytes and print hex=abcd.",
    },
    "qual-cpp-templates": {
        "desc": (
            "Finish the max_sample template so it returns the larger of two values and "
            "main prints max=9. Templates generic-ize DSP helpers across int, float, "
            "and other sample types without copy-paste."
        ),
        "h1": "Compare a and b; return the larger.",
        "h2": "A ternary works: (a > b) ? a : b",
        "h3": "Keep the template <typename T> signature.",
        "expl": (
            "One template serves many numeric types — generic programming for radio math."
        ),
        "goal": "Return the larger value from a template max_sample.",
    },
    "qual-cpp-concurrency": {
        "desc": (
            "A worker thread sets ready=1. Join that thread before reading ready, then "
            "print ready=1. Joining is the handshake that makes shared state safe to "
            "observe after a background IQ worker finishes."
        ),
        "h1": "Call t.join() before printing.",
        "h2": "The lambda already sets ready = 1.",
        "h3": "Do not read ready until after join.",
        "expl": "join waits for the thread; reading shared state earlier is a race.",
        "goal": "Join the worker thread, then print ready=1.",
    },
    "qual-cpp-isr": {
        "desc": (
            "irq_flag is volatile and set by pretend_isr. Call the ISR stub and print "
            "irq=1. volatile tells the compiler a hardware or interrupt path may change "
            "the flag outside normal control flow."
        ),
        "h1": "Keep the volatile qualifier on irq_flag.",
        "h2": "Call pretend_isr() before printing.",
        "h3": "Print irq= followed by the flag value.",
        "expl": (
            "ISR-shared flags are volatile so reads are not optimized into stale registers."
        ),
        "goal": "Set a volatile IRQ flag from a pretend ISR and print irq=1.",
    },
    "qual-gr-overview": {
        "desc": (
            "Read OVERVIEW.txt for the flowgraph qualification path and write "
            "`flowgraph-qualification` into answer.txt. These challenges teach GNU Radio "
            "ideas — blocks, edges, vectors, tone chains — offline without installing GNU Radio."
        ),
        "h1": "OVERVIEW.txt names the track id.",
        "h2": "One line in answer.txt.",
        "h3": "Exact spelling: flowgraph-qualification",
        "expl": (
            "Overview unlocks the offline flowgraph path that mirrors the GNU Radio syllabus."
        ),
        "goal": "Write flowgraph-qualification into answer.txt after reading OVERVIEW.txt.",
    },
    "qual-gr-intro": {
        "desc": (
            "GNU Radio apps are graphs of named blocks. Complete block_name so it returns "
            "the string null_source — a classic source tile with outputs and no inputs. "
            "We practice the catalog idea in plain Python so no GNU Radio install is required."
        ),
        "h1": "Return a string, not a class instance.",
        "h2": "Exact spelling: null_source",
        "h3": "return 'null_source'",
        "expl": "Sources, sinks, and blocks are the vocabulary of a software radio rack.",
        "goal": "Return 'null_source' as the first block catalog card.",
    },
    "qual-gr-flowgraph": {
        "desc": (
            "A flowgraph is a directed set of connections. Implement connect(src, dst) to "
            "record an edge and edges() to return the list of (src, dst) tuples in order. "
            "This is the same connect idea as top_block->connect in GNU Radio C++."
        ),
        "h1": "Store each connection as a (src, dst) tuple.",
        "h2": "append to an internal list in connect.",
        "h3": "edges() returns that list (order preserved).",
        "expl": (
            "Connecting blocks builds the graph; running it later pushes samples along edges."
        ),
        "goal": "Record connections and return them as ordered (src, dst) edges.",
    },
    "qual-gr-vectors": {
        "desc": (
            "Vector blocks process buffers, not scalars. Complete apply_vector_gain so "
            "every sample in the list is multiplied by gain into a new list of equal "
            "length — the same shape as a GNU Radio work() on float vectors."
        ),
        "h1": "Multiply each sample by gain.",
        "h2": "Return a new list; keep length identical.",
        "h3": "[s * gain for s in samples]",
        "expl": (
            "Vector work() calls operate on arrays of samples per call for throughput."
        ),
        "goal": "Scale a float vector by gain (offline stand-in for a vector block).",
    },
    "qual-gr-project": {
        "desc": (
            "Chain two stages like a tiny GNU Radio project: multiply each sample by 2, "
            "then take abs, returning the new list. Real flowgraphs wire gain then "
            "magnitude blocks the same way — we keep it offline and testable with ./check."
        ),
        "h1": "First multiply by 2, then abs.",
        "h2": "A single list comprehension can do both.",
        "h3": "[abs(s * 2) for s in samples]",
        "expl": (
            "Projects chain blocks end-to-end; this challenge is that chain in one function."
        ),
        "goal": "Apply gain 2 then abs to each sample in the tone chain.",
    },
}


class LiteralStr(str):
    pass


def literal_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(LiteralStr, literal_representer)


def dump_challenge(data: dict) -> str:
    """Dump challenge.yaml preserving academy multi-line fields as literals."""
    for key in ("description", "solution", "explanation"):
        if key in data and isinstance(data[key], str):
            data[key] = LiteralStr(data[key].rstrip() + "\n")
    if "extension" in data and isinstance(data["extension"], dict):
        desc = data["extension"].get("description")
        if isinstance(desc, str):
            data["extension"]["description"] = LiteralStr(desc.rstrip() + "\n")
    if "hints" in data:
        for h in data["hints"]:
            if isinstance(h.get("text"), str):
                h["text"] = LiteralStr(h["text"].rstrip() + "\n")
    return yaml.dump(data, sort_keys=False, allow_unicode=True, width=100)


def write_readme(path: Path, title: str, goal: str, edit_target: str, is_overview: bool) -> None:
    if is_overview:
        body = f"""
        {title}
        {'=' * len(title)}

        Goal
        ----
        {goal}

        Steps
        -----
        1) Press Start and open OVERVIEW.txt.
        2) Write the track id into answer.txt (one line).
        3) Prove: ./check
        4) Press Done when check passes.

        Theme
        -----
        Pi SDR Academy qualification path — offline, no Jupyter required.
        """
    else:
        body = f"""
        {title}
        {'=' * len(title)}

        Goal
        ----
        {goal}

        Steps
        -----
        1) Press Start and open {edit_target}.
        2) Make the change described above.
        3) Prove: ./check
        4) Press Done when check passes.

        Theme
        -----
        Qualification topic reshaped as an offline SDR-lab challenge
        (Start → solve → Done). No Jupyter or GNU Radio install required.
        """
    path.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")


def main() -> None:
    missing = []
    for yaml_path in sorted(ROOT.rglob("challenge.yaml")):
        if "qualification" not in str(yaml_path):
            continue
        cid = yaml_path.parent.name
        if cid not in NARRATIVE:
            missing.append(cid)
            continue
        meta = NARRATIVE[cid]
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        data["description"] = meta["desc"]
        data["hints"] = [
            {"level": 1, "text": meta["h1"]},
            {"level": 2, "text": meta["h2"]},
            {"level": 3, "text": meta["h3"]},
        ]
        data["explanation"] = meta["expl"]
        yaml_path.write_text(dump_challenge(data), encoding="utf-8")

        files_dir = yaml_path.parent / "files"
        is_overview = cid.endswith("-overview")
        if is_overview:
            edit_target = "OVERVIEW.txt"
        else:
            skip = {
                "README.txt",
                "check",
                "check.py",
                "run",
                "OVERVIEW.txt",
                "tune.txt",
                "demo.cap",
            }
            starters = sorted(
                p.name
                for p in files_dir.iterdir()
                if p.is_file() and p.name not in skip and not p.name.endswith(".cap")
            )
            # Prefer primary source over headers/packages
            preferred = [s for s in starters if s.endswith((".py", ".cpp"))]
            edit_target = preferred[0] if preferred else (starters[0] if starters else "the starter")
        write_readme(files_dir / "README.txt", data["title"], meta["goal"], edit_target, is_overview)
        print("enriched", cid)

    if missing:
        raise SystemExit(f"missing narratives for: {missing}")
    print("done", len(NARRATIVE))


if __name__ == "__main__":
    main()
