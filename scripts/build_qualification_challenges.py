#!/usr/bin/env python3
"""Build all qualification challenges into curriculum/modules."""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path("/workspace")
MOD = ROOT / "curriculum" / "modules"


def w(path: Path, text: str, exe: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
    if exe:
        path.chmod(0o755)


def yml(cid, module, title, prev, objs, desc, files, tools, flag, hints, sol, expl, diff="easy"):
    pr = "prerequisites: []" if not prev else f"prerequisites:\n- {prev}"
    return f"""id: {cid}
module: {module}
title: {title}
difficulty: {diff}
estimated_time: 20-40 minutes
{pr}
objectives:
{chr(10).join('- '+o for o in objs)}
mastery_evidence:
- understand
- apply
description: |
  {desc}
environment:
  type: workspace
  workspace_subdir: {cid}
  notes: Offline qualification challenge (Pi SDR Academy theme). No Jupyter required.
files:
{chr(10).join('- '+f for f in files)}
expected_tools:
{chr(10).join('- '+t for t in tools)}
flags:
  value: {flag}
  validation: session
hints:
{chr(10).join(f'- level: {i}{chr(10)}  text: |{chr(10)}    {h}' for i,h in enumerate(hints,1))}
solution: |
  {sol}
explanation: |
  {expl}
extension:
  title: Go further
  description: |
    Change one input; keep ./check green without hard-coding.
"""


def py_check(starter: str, body: str) -> str:
    return f'''#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, os
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

spec = importlib.util.spec_from_file_location("student", "{starter}")
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)
{body}
fp = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH","/home/flag.txt"))
fp.parent.mkdir(parents=True, exist_ok=True)
fp.write_text("")
print("CHECK_OK")
'''


def cpp_check(expects: list[str], src_check: str = "pass", pre: str = "") -> str:
    ex = "\n".join(f'if {e!r} not in out: fail("missing "+{e!r})' for e in expects)
    return f'''#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)
{pre}
try:
    subprocess.run(["g++","-std=c++17","-Wall","-Wextra","-O0","-pthread","-o","prog","main.cpp"],
                   check=True, capture_output=True, text=True)
except FileNotFoundError:
    fail("c++ not found")
except subprocess.CalledProcessError as e:
    fail(e.stderr.strip() or "compile failed")
out = subprocess.check_output(["./prog"], text=True, timeout=5)
{ex}
src = Path("main.cpp").read_text(encoding="utf-8")
{src_check}
fp = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH","/home/flag.txt"))
fp.parent.mkdir(parents=True, exist_ok=True)
fp.write_text("")
print("CHECK_OK")
'''


def make_py(mod_dir: Path, module: str, items: list[dict]) -> list[str]:
    ids = []
    prev = None
    for it in items:
        cid = it["id"]
        ids.append(cid)
        b = mod_dir / "challenges" / cid
        files = ["README.txt", it["file"], "run", "check", "check.py"] + [p for p,_ in it.get("extra",[])]
        for rel, body in it.get("extra", []):
            w(b / "files" / rel, body)
        w(b / "challenge.yaml", yml(cid, module, it["title"], prev, it["obj"], it["desc"], files, ["python3"], it["flag"], it["hints"], it["sol"], it["expl"]))
        w(b / "files" / "README.txt", f"""
        {it['title']}
        {'='*len(it['title'])}

        Qualification topic → offline SDR-lab challenge.

        Goal
        ----
        {it['desc']}

        Steps
        -----
        1. Press Start
        2. Edit {it['file']}
        3. ./check
        4. Press Done
        """)
        w(b / "files" / it["file"], it["code"])
        w(b / "files" / "run", "#!/bin/sh\nset -eu\npython3 -c 'print(\"edit starter, then ./check\")'\n", True)
        w(b / "files" / "check", "#!/bin/sh\nexec python3 check.py\n", True)
        w(b / "files" / "check.py", py_check(it["file"], it["check"]), True)
        prev = cid
    return ids


def make_cpp(mod_dir: Path, module: str, items: list[dict]) -> list[str]:
    ids = []
    prev = None
    for it in items:
        cid = it["id"]
        ids.append(cid)
        b = mod_dir / "challenges" / cid
        files = ["README.txt", "main.cpp", "run", "check", "check.py"] + [p for p,_ in it.get("extra",[])]
        for rel, body in it.get("extra", []):
            w(b / "files" / rel, body)
        w(b / "challenge.yaml", yml(cid, module, it["title"], prev, it["obj"], it["desc"], files, ["g++","python3"], it["flag"], it["hints"], it["sol"], it["expl"], "medium"))
        w(b / "files" / "README.txt", f"""
        {it['title']}
        {'='*len(it['title'])}

        C++ qualification → offline SDR-lab challenge.

        Goal
        ----
        {it['desc']}

        Steps
        -----
        1. Press Start
        2. Edit main.cpp
        3. ./run then ./check
        4. Press Done
        """)
        w(b / "files" / "main.cpp", it["code"])
        w(b / "files" / "run", "#!/bin/sh\nset -eu\ng++ -std=c++17 -Wall -Wextra -O0 -pthread -o prog main.cpp && ./prog\n", True)
        w(b / "files" / "check", "#!/bin/sh\nexec python3 check.py\n", True)
        w(b / "files" / "check.py", cpp_check(it["expect"], it.get("src","pass"), it.get("pre","")), True)
        prev = cid
    return ids


# ─── specs ───────────────────────────────────────────────────────────────────

PY = [
 dict(id="qual-py-modules", title="Modules for the Radio Rack", obj=["modules","imports"],
  desc="wavelength_m(mhz) uses math and returns c/f for free-space wavelength.",
  file="radio_math.py",
  code="import math\n\ndef wavelength_m(mhz: float) -> float:\n    # TODO: return 299792458 / (mhz * 1e6)\n    raise NotImplementedError\n",
  check='assert abs(m.wavelength_m(100.0)-299792458/100e6)<1e-6\nassert "math" in Path("radio_math.py").read_text()\n',
  hints=["c=299792458","mhz*1e6","return c/f"], sol="return 299792458/(mhz*1e6)", expl="Modules package reusable radio math.", flag="flag{qual_py_modules}"),
 dict(id="qual-py-types", title="Dynamic Types on the Bench", obj=["dynamic-typing"],
  desc="coerce_samples converts mixed values to list[float].",
  file="samples.py", code="def coerce_samples(values):\n    raise NotImplementedError\n",
  check='assert m.coerce_samples([1,2.5,"3","-4.0"])==[1.0,2.5,3.0,-4.0]\n',
  hints=["float(x)","comprehension","order"], sol="[float(v) for v in values]", expl="Coerce at DSP edges.", flag="flag{qual_py_types}"),
 dict(id="qual-py-oop", title="Classy Signal Meter", obj=["oop","classes"],
  desc="SignalMeter.add and average (0.0 if empty).",
  file="meter.py",
  code="class SignalMeter:\n    def __init__(self):\n        self._r=[]\n    def add(self, power_db: float) -> None:\n        raise NotImplementedError\n    def average(self) -> float:\n        raise NotImplementedError\n",
  check='x=m.SignalMeter(); assert x.average()==0.0\nx.add(10);x.add(20);x.add(30); assert abs(x.average()-20)<1e-9\n',
  hints=["append","sum/len","empty 0"], sol="mean of list", expl="Objects model instruments.", flag="flag{qual_py_oop}"),
 dict(id="qual-py-immutable", title="Frozen IQ Pairs", obj=["immutability"],
  desc="iq_pair returns immutable (i,q) tuple.",
  file="iq.py", code="def iq_pair(i: float, q: float):\n    raise NotImplementedError\n",
  check='p=m.iq_pair(1.0,-1.0); assert isinstance(p,tuple) and p==(1.0,-1.0)\n',
  hints=["tuple","not list","(i,q)"], sol="return (i,q)", expl="Immutability protects samples.", flag="flag{qual_py_immutable}"),
 dict(id="qual-py-refs", title="Alias in the Sample Buffer", obj=["references"],
  desc="share_buffer aliases; mutate_last sets last element in place.",
  file="buffer.py",
  code="def share_buffer(buf: list):\n    raise NotImplementedError\ndef mutate_last(buf: list, value: float) -> None:\n    raise NotImplementedError\n",
  check='a=[1.0,2.0,3.0]; assert m.share_buffer(a) is a\nm.mutate_last(a,9.0); assert a[-1]==9.0\n',
  hints=["return buf","buf[-1]=","no copy"], sol="alias + assign", expl="Names reference objects.", flag="flag{qual_py_refs}"),
 dict(id="qual-py-modern", title="Modern Lab Annotations", obj=["f-strings"],
  desc="format_tune returns 'tune LABEL @ MHz' with 3 decimals.",
  file="tune.py", code="def format_tune(mhz: float, label: str) -> str:\n    raise NotImplementedError\n",
  check='assert m.format_tune(146.52,"NFM")=="tune NFM @ 146.520 MHz"\n',
  hints=["f-string",":.3f","exact text"], sol="f'tune {label} @ {mhz:.3f} MHz'", expl="F-strings clarify logs.", flag="flag{qual_py_modern}"),
 dict(id="qual-py-collections", title="Peak Picker Comprehension", obj=["comprehensions"],
  desc="peaks_above returns indices where sample > thresh.",
  file="peaks.py", code="def peaks_above(samples, thresh: float):\n    raise NotImplementedError\n",
  check='assert m.peaks_above([0.1,0.9,0.2,1.1,0.0],0.5)==[1,3]\n',
  hints=["enumerate","comprehension","indices"], sol="[i for i,s in enumerate(samples) if s>thresh]", expl="Comprehensions filter streams.", flag="flag{qual_py_collections}"),
 dict(id="qual-py-context", title="Context-Managed Capture", obj=["context-managers"],
  desc="read_capture uses with-open and returns stripped text.",
  file="capture.py", code="def read_capture(path: str) -> str:\n    raise NotImplementedError\n",
  check='Path("demo.cap").write_text("  iq-burst  \\n",encoding="utf-8")\nassert m.read_capture("demo.cap")=="iq-burst"\nassert "with" in Path("capture.py").read_text()\n',
  hints=["with open","strip","context"], sol="with open as f: return f.read().strip()", expl="with is RAII for files.", flag="flag{qual_py_context}"),
 dict(id="qual-py-exceptions", title="Safe Flag Parse", obj=["exceptions"],
  desc="parse_flag returns flag{...} or raises ValueError.",
  file="flags.py", code="def parse_flag(text: str) -> str:\n    raise NotImplementedError\n",
  check='assert m.parse_flag(" flag{ok} ")=="flag{ok}"\ntry:\n m.parse_flag("x"); fail("no raise")\nexcept ValueError:\n pass\n',
  hints=["strip","flag{...","}","ValueError"], sol="validate or raise", expl="Exceptions beat silent None.", flag="flag{qual_py_exceptions}"),
 dict(id="qual-py-packaging", title="Tiny Package Layout", obj=["packages"],
  desc="load_version imports labkit and returns version.",
  file="labkit_loader.py", code="def load_version() -> str:\n    raise NotImplementedError\n",
  extra=[("labkit/__init__.py","version = '1.0.0'\n")],
  check='assert m.load_version()=="1.0.0"\nassert Path("labkit/__init__.py").is_file()\n',
  hints=["import labkit","version","keep pkg"], sol="return labkit.version", expl="Packages structure toolkits.", flag="flag{qual_py_packaging}"),
 dict(id="qual-py-bits", title="Pack a Beacon Header", obj=["struct","endianness"],
  desc="pack_header packs two big-endian uint16 values.",
  file="beacon.py", code="import struct\ndef pack_header(seq: int, code: int) -> bytes:\n    raise NotImplementedError\n",
  check='assert m.pack_header(1,0xABCD)==bytes.fromhex("0001abcd")\n',
  hints=[">HH","struct.pack","BE"], sol="struct.pack('>HH',seq,code)", expl="Wire formats are bytes.", flag="flag{qual_py_bits}"),
 dict(id="qual-py-dataclass", title="Dataclass Frame Log", obj=["dataclasses","json"],
  desc="to_json serializes Frame via asdict.",
  file="frame.py",
  code="from dataclasses import dataclass, asdict\nimport json\n@dataclass\nclass Frame:\n    freq_mhz: float\n    note: str\ndef to_json(frame: Frame) -> str:\n    raise NotImplementedError\n",
  check='import json\nassert json.loads(m.to_json(m.Frame(146.52,"call")))=={"freq_mhz":146.52,"note":"call"}\n',
  hints=["asdict","json.dumps","fields"], sol="json.dumps(asdict(frame))", expl="Dataclasses serialize cleanly.", flag="flag{qual_py_dataclass}"),
 dict(id="qual-py-decorators", title="Decorator Call Counter", obj=["decorators"],
  desc="counted(fn) wrapper exposes .calls starting at 0.",
  file="timing.py", code="def counted(fn):\n    raise NotImplementedError\n",
  check='@m.counted\ndef add(a,b):\n return a+b\nassert add(2,3)==5 and add.calls==1\nassert add(0,0)==0 and add.calls==2\n',
  hints=["wrapper","calls=0","increment"], sol="decorator increments calls", expl="Decorators wrap cross-cuts.", flag="flag{qual_py_decorators}"),
 dict(id="qual-py-typing", title="Typed Gain Stage", obj=["type-hints"],
  desc="apply_gain multiplies each sample by gain.",
  file="gain.py",
  code="from __future__ import annotations\ndef apply_gain(samples: list[float], gain: float) -> list[float]:\n    raise NotImplementedError\n",
  check='assert m.apply_gain([1.0,-2.0,0.5],2.0)==[2.0,-4.0,1.0]\n',
  hints=["comprehension","s*gain","new list"], sol="[s*gain for s in samples]", expl="Hints document contracts.", flag="flag{qual_py_typing}"),
]

CPP = [
 dict(id="qual-cpp-namespaces", title="Namespace the Calculator", obj=["namespaces"],
  desc="RadioMath::sub returns a-b; program prints sum and diff.",
  code="""#include <iostream>
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
}
""",
  expect=["sum=15","diff=5"], src='assert "namespace RadioMath" in src\n',
  hints=["return a-b","keep namespace","RadioMath::"], sol="sub returns a-b", expl="Namespaces scale radio codebases.", flag="flag{qual_cpp_namespaces}"),
 dict(id="qual-cpp-data", title="Tune File In C++", obj=["strings","fstream"],
  desc="Read first line of tune.txt and print tune=<line>.",
  extra=[("tune.txt","146.52\n")],
  code="""#include <fstream>
#include <iostream>
#include <string>
int main() {
  std::ifstream in("tune.txt");
  std::string line;
  if (!std::getline(in, line)) return 1;
  // TODO: already reading — ensure output format tune=<line>
  std::cout << "tune=" << line << "\\n";
}
""",
  expect=["tune=146.52"], src='assert "getline" in src\n',
  hints=["tune.txt provided","getline","tune="], sol="getline + print", expl="Files carry operator notes.", flag="flag{qual_cpp_data}"),
 dict(id="qual-cpp-oop", title="Tone Synthesizer Class", obj=["oop","classes"],
  desc="class Tone with freq() accessor printing freq=440.",
  code="""#include <iostream>
class Tone {
  int hz_;
public:
  explicit Tone(int hz) : hz_(hz) {}
  int freq() const {
    // TODO: return hz_
    return 0;
  }
};
int main() {
  Tone t(440);
  std::cout << "freq=" << t.freq() << "\\n";
}
""",
  expect=["freq=440"], src='assert "class Tone" in src\n',
  hints=["return hz_","const method","ctor sets hz_"], sol="return hz_", expl="Classes encapsulate signal state.", flag="flag{qual_cpp_oop}"),
 dict(id="qual-cpp-const", title="Const Gain Path", obj=["const","qualifiers"],
  desc="scale_const uses const ref input and prints scaled=6.",
  code="""#include <iostream>
int scale_const(const int& sample, int gain) {
  // TODO: return sample * gain (sample is const — do not assign to it)
  return 0;
}
int main() {
  int s = 3;
  std::cout << "scaled=" << scale_const(s, 2) << "\\n";
}
""",
  expect=["scaled=6"], src='assert "const int" in src\n',
  hints=["return sample*gain","const ref","no mutate"], sol="return sample*gain", expl="const documents read-only paths.", flag="flag{qual_cpp_const}"),
 dict(id="qual-cpp-pointers", title="Pointer to the Sample", obj=["pointers","references"],
  desc="Set *p to 42 and print value=42.",
  code="""#include <iostream>
int main() {
  int sample = 0;
  int* p = &sample;
  // TODO: write 42 through the pointer
  std::cout << "value=" << sample << "\\n";
}
""",
  expect=["value=42"], src='assert "*" in src and "&" in src\n',
  hints=["*p = 42","pointer","address-of"], sol="*p=42", expl="Pointers address live samples.", flag="flag{qual_cpp_pointers}"),
 dict(id="qual-cpp-modern", title="Auto and Range-For", obj=["modern-cpp","auto"],
  desc="Sum gains with range-for and print sum=6.",
  code="""#include <iostream>
#include <vector>
int main() {
  std::vector<int> gains{1, 2, 3};
  int sum = 0;
  // TODO: range-for over gains adding into sum
  for (int g : gains) {
    sum += g;
  }
  std::cout << "sum=" << sum << "\\n";
}
""",
  expect=["sum=6"], src='assert ":" in src\n',
  hints=["for (int g : gains)","sum+=g","keep print"], sol="range-for sum", expl="Modern C++ prefers range-for.", flag="flag{qual_cpp_modern}"),
 dict(id="qual-cpp-stl", title="STL Peak Scan", obj=["stl","algorithms"],
  desc="Use std::max_element to print peak=9.",
  code="""#include <algorithm>
#include <iostream>
#include <vector>
int main() {
  std::vector<int> v{1, 9, 3, 7};
  // TODO: auto it = std::max_element(v.begin(), v.end());
  auto it = std::max_element(v.begin(), v.end());
  std::cout << "peak=" << *it << "\\n";
}
""",
  expect=["peak=9"], src='assert "max_element" in src\n',
  hints=["max_element","dereference it","include algorithm"], sol="max_element", expl="STL algorithms beat hand loops.", flag="flag{qual_cpp_stl}"),
 dict(id="qual-cpp-raii", title="RAII File Guard", obj=["raii","smart-pointers"],
  desc="Use unique_ptr<int> holding 7 and print owned=7.",
  code="""#include <iostream>
#include <memory>
int main() {
  // TODO: std::unique_ptr<int> p(new int(7));  or make_unique
  std::unique_ptr<int> p = std::make_unique<int>(7);
  std::cout << "owned=" << *p << "\\n";
}
""",
  expect=["owned=7"], src='assert "unique_ptr" in src\n',
  hints=["make_unique","unique_ptr","dereference"], sol="unique_ptr owns int(7)", expl="RAII frees on scope exit.", flag="flag{qual_cpp_raii}"),
 dict(id="qual-cpp-errors", title="Throw on Bad Gain", obj=["exceptions"],
  desc="apply_gain throws std::invalid_argument on negative gain; main prints ok=8.",
  code="""#include <iostream>
#include <stdexcept>
int apply_gain(int sample, int gain) {
  if (gain < 0) throw std::invalid_argument("gain");
  return sample * gain;
}
int main() {
  try {
    int v = apply_gain(4, 2);
    std::cout << "ok=" << v << "\\n";
    apply_gain(1, -1);
    std::cout << "should_not_print\\n";
  } catch (const std::invalid_argument&) {
    std::cout << "caught\\n";
  }
}
""",
  expect=["ok=8","caught"], src='assert "throw" in src\n',
  hints=["already almost done","keep throw","catch"], sol="throw invalid_argument", expl="Exceptions signal bad operator input.", flag="flag{qual_cpp_errors}"),
 dict(id="qual-cpp-cmake", title="CMake-Style Target Name", obj=["cmake","build-systems"],
  desc="Print target=beacon_rx to mimic a CMake target name constant.",
  code="""#include <iostream>
#include <string>
int main() {
  // Pretend this string is your CMake target name
  std::string target = "beacon_rx";
  std::cout << "target=" << target << "\\n";
}
""",
  expect=["target=beacon_rx"], src='assert "beacon_rx" in src\n',
  hints=["set string","print target=","keep name"], sol="print target", expl="Build systems name radio binaries.", flag="flag{qual_cpp_cmake}"),
 dict(id="qual-cpp-packages", title="Vendored Header Include", obj=["packages","headers"],
  desc="Include local labkit.hpp and print ver=1.",
  extra=[("labkit.hpp","#pragma once\ninline int labkit_version(){return 1;}\n")],
  code="""#include <iostream>
#include "labkit.hpp"
int main() {
  std::cout << "ver=" << labkit_version() << "\\n";
}
""",
  expect=["ver=1"], src='assert "labkit.hpp" in src\n',
  hints=["include labkit.hpp","call labkit_version","quotes include"], sol="include local header", expl="Packages ship headers beside sources.", flag="flag{qual_cpp_packages}"),
 dict(id="qual-cpp-bits", title="Pack Big-Endian ID", obj=["bit-manipulation"],
  desc="Pack uint16 0xABCD as big-endian bytes and print hex=abcd.",
  code="""#include <cstdint>
#include <iostream>
int main() {
  uint16_t id = 0xABCD;
  uint8_t hi = static_cast<uint8_t>((id >> 8) & 0xFF);
  uint8_t lo = static_cast<uint8_t>(id & 0xFF);
  std::cout << std::hex << "hex=" << int(hi) << int(lo) << "\\n";
}
""",
  expect=["hex=abcd"], src='assert ">>" in src\n',
  hints=["shift 8","mask 0xFF","hex out"], sol="hi/lo bytes", expl="Bit ops build beacon headers.", flag="flag{qual_cpp_bits}"),
 dict(id="qual-cpp-templates", title="Template Max Sample", obj=["templates"],
  desc="Template max_sample prints max=9 for ints.",
  code="""#include <iostream>
template <typename T>
T max_sample(T a, T b) {
  // TODO: return the larger of a and b
  return (a > b) ? a : b;
}
int main() {
  std::cout << "max=" << max_sample(3, 9) << "\\n";
}
""",
  expect=["max=9"], src='assert "template" in src\n',
  hints=["ternary","template <typename T>","return larger"], sol="return a>b?a:b", expl="Templates generic-ize DSP helpers.", flag="flag{qual_cpp_templates}"),
 dict(id="qual-cpp-concurrency", title="Thread the Increment", obj=["threads","concurrency"],
  desc="Launch a thread that sets ready=1; join; print ready=1.",
  code="""#include <iostream>
#include <thread>
int main() {
  int ready = 0;
  std::thread t([&]() { ready = 1; });
  // TODO: join the thread before reading ready
  t.join();
  std::cout << "ready=" << ready << "\\n";
}
""",
  expect=["ready=1"], src='assert "join" in src && "thread" in src\n',
  hints=["t.join()","capture ready","include thread"], sol="join before print", expl="Join before observing shared state.", flag="flag{qual_cpp_concurrency}"),
 dict(id="qual-cpp-isr", title="ISR Flag Handshake", obj=["isr","volatile"],
  desc="volatile irq_flag set by pretend ISR; main prints irq=1.",
  code="""#include <iostream>
volatile int irq_flag = 0;
void pretend_isr() { irq_flag = 1; }
int main() {
  pretend_isr();
  std::cout << "irq=" << irq_flag << "\\n";
}
""",
  expect=["irq=1"], src='assert "volatile" in src\n',
  hints=["volatile already","call pretend_isr","print irq="], sol="volatile flag", expl="volatile for ISR-shared flags.", flag="flag{qual_cpp_isr}"),
]

FLOW = [
 dict(id="qual-gr-intro", title="Block Catalog Card", obj=["flowgraph-basics"],
  desc="block_name() returns 'null_source' — first tile in a software radio rack.",
  file="blocks.py",
  code="def block_name() -> str:\n    # TODO: return the string null_source\n    raise NotImplementedError\n",
  check='assert m.block_name()=="null_source"\n',
  hints=["return 'null_source'","exact spelling","string"], sol="return 'null_source'", expl="GNU Radio apps are graphs of named blocks — we practice the idea offline.", flag="flag{qual_gr_intro}"),
 dict(id="qual-gr-flowgraph", title="Connect the Flowgraph", obj=["connections"],
  desc="connect(src,dst) records an edge; edges() returns list of (src,dst).",
  file="graph.py",
  code="class FlowGraph:\n    def __init__(self):\n        self._e=[]\n    def connect(self, src: str, dst: str) -> None:\n        raise NotImplementedError\n    def edges(self):\n        raise NotImplementedError\n",
  check='g=m.FlowGraph(); g.connect("src","sink"); assert g.edges()==[("src","sink")]\n',
  hints=["append tuple","return list","order preserved"], sol="store edges list", expl="Flowgraphs are directed edges between blocks.", flag="flag{qual_gr_flowgraph}"),
 dict(id="qual-gr-vectors", title="Vector Block Gain", obj=["vector-blocks","dsp"],
  desc="apply_vector_gain(samples, gain) scales a float vector (block work()).",
  file="vector_block.py",
  code="def apply_vector_gain(samples, gain: float):\n    raise NotImplementedError\n",
  check='assert m.apply_vector_gain([1.0,2.0,-1.0],0.5)==[0.5,1.0,-0.5]\n',
  hints=["comprehension","s*gain","same length"], sol="[s*gain for s in samples]", expl="Vector blocks process buffers, not scalars.", flag="flag{qual_gr_vectors}"),
 dict(id="qual-gr-project", title="Tone Processor Chain", obj=["signal-chain"],
  desc="process_tone(samples) applies gain 2 then abs — a tiny tone chain.",
  file="tone_chain.py",
  code="def process_tone(samples):\n    # TODO: each sample -> abs(sample * 2)\n    raise NotImplementedError\n",
  check='assert m.process_tone([1.0,-3.0,0.5])==[2.0,6.0,1.0]\n',
  hints=["*2","abs","list comp"], sol="[abs(s*2) for s in samples]", expl="Projects chain blocks: gain then magnitude.", flag="flag{qual_gr_project}"),
]


def write_module(order: int, folder: str, slug: str, title: str, desc: str, prereq: list[str], ids: list[str]) -> None:
    path = MOD / folder
    pr = "\n".join(f"- {p}" for p in prereq) if prereq else "[]"
    if prereq:
        pr_block = "prerequisites:\n" + "\n".join(f"- {p}" for p in prereq)
    else:
        pr_block = "prerequisites: []"
    w(path / "module.yaml", f"""
    id: {slug}
    slug: {slug}
    title: {title}
    order: {order}
    description: |
      {desc}
    {pr_block}
    challenges:
{chr(10).join(f'    - {i}' for i in ids)}
    """)


def main() -> None:
    py_dir = MOD / "12-python-qualification"
    cpp_dir = MOD / "13-cpp-qualification"
    gr_dir = MOD / "14-flowgraph-qualification"

    py_ids = make_py(py_dir, "python-qualification", PY)
    write_module(12, "12-python-qualification", "python-qualification", "Python Qualification",
                 "Professional Python qualification topics as offline SDR-lab challenges.",
                 ["python"], py_ids)

    cpp_ids = make_cpp(cpp_dir, "cpp-qualification", CPP)
    write_module(13, "13-cpp-qualification", "cpp-qualification", "C++ Qualification",
                 "Professional C++ qualification topics as offline SDR-lab challenges.",
                 ["c"], cpp_ids)

    # flowgraph uses python emitter shape
    gr_items = []
    for it in FLOW:
        gr_items.append(dict(
            id=it["id"], title=it["title"], obj=it["obj"], desc=it["desc"],
            file=it["file"], code=it["code"], check=it["check"],
            hints=it["hints"], sol=it["sol"], expl=it["expl"], flag=it["flag"],
        ))
    gr_ids = make_py(gr_dir, "flowgraph-qualification", gr_items)
    write_module(14, "14-flowgraph-qualification", "flowgraph-qualification", "Flowgraph Qualification",
                 "GNU Radio qualification ideas — blocks, edges, vectors, tone chain — without requiring GNU Radio installed.",
                 ["dsp-fundamentals"], gr_ids)

    print("python", len(py_ids))
    print("cpp", len(cpp_ids))
    print("flow", len(gr_ids))
    print("total new", len(py_ids)+len(cpp_ids)+len(gr_ids))


if __name__ == "__main__":
    main()
