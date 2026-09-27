#!/usr/bin/env python3
"""Generate offline qualification challenges (Python, C++, Flowgraph) for Pi SDR Academy."""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "curriculum" / "modules"


def write(path: Path, text: str, *, exe: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
    if exe:
        path.chmod(0o755)


def emit_yaml(cid, module, title, prereq, objectives, desc, files, tools, flag, hints, solution, explanation, difficulty="easy"):
    pr = "prerequisites: []" if not prereq else "prerequisites:\n" + "\n".join(f"- {p}" for p in prereq)
    return f"""id: {cid}
module: {module}
title: {title}
difficulty: {difficulty}
estimated_time: 20-40 minutes
{pr}
objectives:
{chr(10).join(f'- {o}' for o in objectives)}
mastery_evidence:
- understand
- apply
description: |
  {desc}
environment:
  type: workspace
  workspace_subdir: {cid}
  notes: Offline qualification challenge for Pi SDR Academy. No Jupyter / GNU Radio install required.
files:
{chr(10).join(f'- {f}' for f in files)}
expected_tools:
{chr(10).join(f'- {t}' for t in tools)}
flags:
  value: {flag}
  validation: session
hints:
{chr(10).join(f'- level: {i}{chr(10)}  text: |{chr(10)}    {h}' for i, h in enumerate(hints, 1))}
solution: |
  {solution}
explanation: |
  {explanation}
extension:
  title: Go further
  description: |
    Change one input and keep ./check green without hard-coding.
"""


def emit_py(module_slug: str, module_dir: Path, specs: list[dict]) -> list[str]:
    ids: list[str] = []
    prev = None
    for spec in specs:
        cid = spec["cid"]
        ids.append(cid)
        base = module_dir / "challenges" / cid
        starter_name, starter = spec["starter"]
        files = ["README.txt", starter_name, "run", "check", "check.py"]
        for rel, body in spec.get("extra", []):
            write(base / "files" / rel, body)
            files.append(rel)
        write(
            base / "challenge.yaml",
            emit_yaml(
                cid,
                module_slug,
                spec["title"],
                [prev] if prev else [],
                spec["objectives"],
                spec["desc"],
                files,
                ["python3"],
                spec["flag"],
                spec["hints"],
                spec["solution"],
                spec["explanation"],
                spec.get("difficulty", "easy"),
            ),
        )
        write(
            base / "files" / "README.txt",
            f"""
            {spec['title']}
            {'=' * len(spec['title'])}

            From the qualification syllabus — rewritten as an offline SDR-lab puzzle.

            Goal
            ----
            {spec['desc']}

            Steps
            -----
            1. Press Start.
            2. Edit {starter_name}.
            3. Run ./check until CHECK_OK.
            4. Press Done in the dojo.
            """,
        )
        write(base / "files" / starter_name, starter)
        write(base / "files" / "run", "#!/bin/sh\nset -eu\npython3 -c 'print(\"edit the starter, then ./check\")'\n", exe=True)
        write(base / "files" / "check", "#!/bin/sh\nexec python3 check.py\n", exe=True)
        write(
            base / "files" / "check.py",
            f'''#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, os
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

spec = importlib.util.spec_from_file_location("student", "{starter_name}")
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

{spec["check"]}

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
''',
            exe=True,
        )
        prev = cid
    return ids


def emit_cpp(module_slug: str, module_dir: Path, specs: list[dict]) -> list[str]:
    ids: list[str] = []
    prev = None
    for spec in specs:
        cid = spec["cid"]
        ids.append(cid)
        base = module_dir / "challenges" / cid
        files = ["README.txt", "main.cpp", "run", "check", "check.py"]
        extra = spec.get("cxxflags", "")
        write(
            base / "challenge.yaml",
            emit_yaml(
                cid,
                module_slug,
                spec["title"],
                [prev] if prev else [],
                spec["objectives"],
                spec["desc"],
                files,
                ["c++", "python3"],
                spec["flag"],
                spec["hints"],
                spec["solution"],
                spec["explanation"],
                spec.get("difficulty", "medium"),
            ),
        )
        write(
            base / "files" / "README.txt",
            f"""
            {spec['title']}
            {'=' * len(spec['title'])}

            C++ qualification topic — SDR-lab themed, offline (no Jupyter).

            Goal
            ----
            {spec['desc']}

            Steps
            -----
            1. Press Start.
            2. Edit main.cpp.
            3. ./run then ./check.
            4. Press Done.
            """,
        )
        write(base / "files" / "main.cpp", spec["starter"])
        flags = f" {extra}" if extra else ""
        write(base / "files" / "run", f"#!/bin/sh\nset -eu\nc++ -std=c++17 -Wall -Wextra -O0{flags} -o prog main.cpp && ./prog\n", exe=True)
        write(base / "files" / "check", "#!/bin/sh\nexec python3 check.py\n", exe=True)
        expect_lines = "\n".join(f'if {s!r} not in out: fail("missing: " + {s!r})' for s in spec["expect"])
        src_check = spec.get("source_check", "pass")
        cxx_list = '", "'.join(["c++", "-std=c++17", "-Wall", "-Wextra", "-O0"] + ([extra] if extra else []) + ["-o", "prog", "main.cpp"])
        write(
            base / "files" / "check.py",
            f'''#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

cmd = ["{cxx_list}"]
# rebuild list properly
cmd = ["c++", "-std=c++17", "-Wall", "-Wextra", "-O0"] + ({repr([extra])} if {bool(extra)} else []) + ["-o", "prog", "main.cpp"]
try:
    subprocess.run(cmd, check=True, capture_output=True, text=True)
except FileNotFoundError:
    fail("c++ not found")
except subprocess.CalledProcessError as e:
    fail(e.stderr.strip() or "compile failed")
try:
    out = subprocess.check_output(["./prog"], text=True, timeout=5)
except Exception as e:
    fail(str(e))
{expect_lines}
src = Path("main.cpp").read_text(encoding="utf-8")
{src_check}
flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
''',
            exe=True,
        )
        prev = cid
    return ids


def module_yaml(path: Path, slug: str, title: str, order: int, desc: str, prereq: list[str], ids: list[str]) -> None:
    write(
        path / "module.yaml",
        f"""
        id: {slug}
        slug: {slug}
        title: {title}
        order: {order}
        description: |
          {desc}
        prerequisites:
{chr(10).join(f'        - {p}' for p in prereq) if prereq else '        []'}
        challenges:
{chr(10).join(f'        - {c}' for c in ids)}
        """.replace("        []", "[]") if not prereq else f"""
        id: {slug}
        slug: {slug}
        title: {title}
        order: {order}
        description: |
          {desc}
        prerequisites:
{chr(10).join(f'        - {p}' for p in prereq)}
        challenges:
{chr(10).join(f'        - {c}' for c in ids)}
        """,
    )


def python_specs() -> list[dict]:
    return [
        dict(cid="qual-py-modules", title="Modules for the Radio Rack", objectives=["modules", "imports"],
             desc="Implement wavelength_m(mhz) using the math module (c/f).",
             starter=("radio_math.py", "import math\n\ndef wavelength_m(mhz: float) -> float:\n    # TODO: return 299792458 / (mhz * 1e6)\n    raise NotImplementedError\n"),
             check='got=m.wavelength_m(100.0)\nif abs(got-299792458/100e6)>1e-6: fail(str(got))\nif "math" not in Path("radio_math.py").read_text(): fail("import math")\n',
             hints=["c = 299792458", "f = mhz*1e6", "return c/f"], solution="return 299792458/(mhz*1e6)",
             explanation="Modules keep radio math reusable.", flag="flag{qual_py_modules}"),
        dict(cid="qual-py-types", title="Dynamic Types on the Bench", objectives=["dynamic-typing"],
             desc="coerce_samples turns mixed values into list[float].",
             starter=("samples.py", "def coerce_samples(values):\n    raise NotImplementedError\n"),
             check='if m.coerce_samples([1,2.5,"3","-4.0"])!=[1.0,2.5,3.0,-4.0]: fail("coerce")\n',
             hints=["float(x)", "list comprehension", "preserve order"], solution="[float(v) for v in values]",
             explanation="Coerce at DSP boundaries.", flag="flag{qual_py_types}"),
        dict(cid="qual-py-oop", title="Classy Signal Meter", objectives=["classes", "oop"],
             desc="SignalMeter.add / average (0.0 if empty).",
             starter=("meter.py", "class SignalMeter:\n    def __init__(self):\n        self._r=[]\n    def add(self, power_db: float) -> None:\n        raise NotImplementedError\n    def average(self) -> float:\n        raise NotImplementedError\n"),
             check='x=m.SignalMeter()\nassert x.average()==0.0\nx.add(10);x.add(20);x.add(30)\nassert abs(x.average()-20)<1e-9\n',
             hints=["append", "sum/len", "empty→0"], solution="store list; mean", explanation="Objects model instruments.", flag="flag{qual_py_oop}"),
        dict(cid="qual-py-immutable", title="Frozen IQ Pairs", objectives=["immutability"],
             desc="iq_pair returns immutable (i,q) tuple.",
             starter=("iq.py", "def iq_pair(i: float, q: float):\n    raise NotImplementedError\n"),
             check='p=m.iq_pair(1.0,-1.0)\nassert isinstance(p,tuple) and p==(1.0,-1.0)\n',
             hints=["tuple", "not list", "return (i,q)"], solution="return (i,q)", explanation="Immutability protects samples.", flag="flag{qual_py_immutable}"),
        dict(cid="qual-py-refs", title="Alias in the Sample Buffer", objectives=["references"],
             desc="share_buffer aliases the list; mutate_last edits last element in place.",
             starter=("buffer.py", "def share_buffer(buf: list):\n    raise NotImplementedError\ndef mutate_last(buf: list, value: float) -> None:\n    raise NotImplementedError\n"),
             check='a=[1.0,2.0,3.0]\nassert m.share_buffer(a) is a\nm.mutate_last(a,9.0)\nassert a[-1]==9.0\n',
             hints=["return buf", "buf[-1]=value", "no copy"], solution="alias + in-place set", explanation="Names reference objects.", flag="flag{qual_py_refs}"),
        dict(cid="qual-py-modern", title="Modern Lab Annotations", objectives=["f-strings"],
             desc="format_tune → 'tune LABEL @ MHz' with 3 decimals via f-string.",
             starter=("tune.py", "def format_tune(mhz: float, label: str) -> str:\n    raise NotImplementedError\n"),
             check='assert m.format_tune(146.52,"NFM")=="tune NFM @ 146.520 MHz"\n',
             hints=["f-string", "{mhz:.3f}", "exact text"], solution="f'tune {label} @ {mhz:.3f} MHz'", explanation="F-strings clarify logs.", flag="flag{qual_py_modern}"),
        dict(cid="qual-py-collections", title="Peak Picker Comprehension", objectives=["comprehensions"],
             desc="peaks_above returns indices where sample > thresh.",
             starter=("peaks.py", "def peaks_above(samples, thresh: float):\n    raise NotImplementedError\n"),
             check='assert m.peaks_above([0.1,0.9,0.2,1.1,0.0],0.5)==[1,3]\n',
             hints=["enumerate", "comprehension", "indices"], solution="[i for i,s in enumerate(samples) if s>thresh]", explanation="Comprehensions filter streams.", flag="flag{qual_py_collections}"),
        dict(cid="qual-py-context", title="Context-Managed Capture", objectives=["context-managers"],
             desc="read_capture uses with open and returns stripped text.",
             starter=("capture.py", "def read_capture(path: str) -> str:\n    raise NotImplementedError\n"),
             check='Path("demo.cap").write_text("  iq-burst  \\n",encoding="utf-8")\nassert m.read_capture("demo.cap")=="iq-burst"\nassert "with" in Path("capture.py").read_text()\n',
             hints=["with open", "strip", "context manager"], solution="with open as f: return f.read().strip()", explanation="with = RAII for files.", flag="flag{qual_py_context}"),
        dict(cid="qual-py-exceptions", title="Safe Flag Parse", objectives=["exceptions"],
             desc="parse_flag returns flag{...} or raises ValueError.",
             starter=("flags.py", "def parse_flag(text: str) -> str:\n    raise NotImplementedError\n"),
             check='assert m.parse_flag(" flag{ok} ")=="flag{ok}"\n\ntry:\n m.parse_flag("x"); fail("no raise")\nexcept ValueError:\n pass\n',
             hints=["strip", "flag{", "ValueError"], solution="validate or raise", explanation="Exceptions beat silent failure.", flag="flag{qual_py_exceptions}"),
        dict(cid="qual-py-packaging", title="Tiny Package Layout", objectives=["packages"],
             desc="load_version imports labkit and returns version.",
             starter=("labkit_loader.py", "def load_version() -> str:\n    raise NotImplementedError\n"),
             extra=[("labkit/__init__.py", "version = '1.0.0'\n")],
             check='assert m.load_version()=="1.0.0"\nassert Path("labkit/__init__.py").is_file()\n',
             hints=["import labkit", "labkit.version", "keep package"], solution="return labkit.version", explanation="Packages structure toolkits.", flag="flag{qual_py_packaging}"),
        dict(cid="qual-py-bits", title="Pack a Beacon Header", objectives=["struct", "endianness"],
             desc="pack_header(seq,code) packs two big-endian uint16s.",
             starter=("beacon.py", "import struct\ndef pack_header(seq: int, code: int) -> bytes:\n    raise NotImplementedError\n"),
             check='assert m.pack_header(1,0xABCD)==bytes.fromhex("0001abcd")\n',
             hints=[">HH", "struct.pack", "big-endian"], solution="struct.pack('>HH',seq,code)", explanation="Wire formats are bytes.", flag="flag{qual_py_bits}"),
        dict(cid="qual-py-dataclass", title="Dataclass Frame Log", objectives=["dataclasses", "json"],
             desc="Frame dataclass + to_json via asdict.",
             starter=("frame.py", "from dataclasses import dataclass, asdict\nimport json\n@dataclass\nclass Frame:\n    freq_mhz: float\n    note: str\ndef to_json(frame: Frame) -> str:\n    raise NotImplementedError\n"),
             check='import json\nassert json.loads(m.to_json(m.Frame(146.52,"call")))=={"freq_mhz":146.52,"note":"call"}\n',
             hints=["asdict", "json.dumps", "Frame fields"], solution="json.dumps(asdict(frame))", explanation="Dataclasses serialize cleanly.", flag="flag{qual_py_dataclass}"),
        dict(cid="qual-py-decorators", title="Decorator Call Counter", objectives=["decorators"],
             desc="counted(fn) wrapper with .calls starting at 0.",
             starter=("timing.py", "def counted(fn):\n    raise NotImplementedError\n"),
             check='@m.counted\ndef add(a,b):\n return a+b\nassert add(2,3)==5 and add.calls==1\nassert add(0,0)==0 and add.calls==2\n',
             hints=["wrapper", "calls=0", "increment"], solution="decorator increments calls", explanation="Decorators wrap cross-cuts.", flag="flag{qual_py_decorators}"),
        dict(cid="qual-py-typing", title="Typed Gain Stage", objectives=["type-hints"],
             desc="apply_gain(samples, gain) multiplies each sample.",
             starter=("gain.py", "from __future__ import annotations\ndef apply_gain(samples: list[float], gain: float) -> list[float]:\n    raise NotImplementedError\n"),
             check='assert m.apply_gain([1.0,-2.0,0.5],2.0)==[2.0,-4.0,1.0]\n',
             hints=["comprehension", "s*gain", "new list"], solution="[s*gain for s in samples]", explanation="Hints document contracts.", flag="flag{qual_py_typing}"),
    ]


def cpp_specs() -> list[dict]:
    return [
        dict(cid="qual-cpp-namespaces", title="Namespace the Calculator", objectives=["namespaces"],
             desc="Create namespace RadioMath with add/sub that main prints.",
             starter="""#include <iostream>
namespace RadioMath {
  int add(int a, int b) { return a + b; }
  int sub(int a, int b) {
    // TODO: return a - b
    return 0;
  }
}
int main() {
  std::cout << "sum=" << RadioMath::add(10, 5) << "\\n";
  std::cout << "diff=" << RadioMath::sub(10, 5) << "\\n";
  return 0;
}
""",
             expect=["sum=15", "diff=5"], source_check='if "namespace RadioMath" not in src: fail("namespace")',
             hints=["return a-b", "Keep namespace", "Use RadioMath::"], solution="sub returns a-b", explanation="Namespaces avoid name clashes in big radio stacks.", flag="flag{qual_cpp_namespaces}"),
        dict(cid="qual-cpp-data", title="Tune File In C++", objectives=["strings", "fstream"],
             desc="Read tune.txt first line and print tune=<line>.",
             starter="""#include <fstream>
#include <iostream>
#include <string>
int main() {
  std::ifstream in("tune.txt");
  std::string line;
  // TODO: read one line from in into line
  if (!std::getline(in, line)) return 1;
  std::cout << "tune=" << line << "\\n";
  return 0;
}
""",
             expect=["tune=146.52"], source_check='Path("tune.txt").write_text("146.52\\n", encoding="utf-8")\n# re-run after writing file\\n'
             # Actually check writes file before run - fix in check by writing before execute - handle in starter shipping tune.txt
             ,
             hints=["getline", "tune.txt shipped", "print tune="], solution="getline + print", explanation="Files carry operator notes.", flag="flag{qual_cpp_data}",
             # We'll add tune.txt as note - modify emit to support extra files for cpp... ship via rewriting check to write file first
             ),
    ]


if __name__ == "__main__":
    print("use gen_all below")
