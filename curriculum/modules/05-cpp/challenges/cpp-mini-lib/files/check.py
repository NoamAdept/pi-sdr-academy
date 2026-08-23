#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

Path("test_student.cpp").write_text('#include "include/signal/channel_plan.hpp"\n#include "include/signal/frequency.hpp"\n#include <cassert>\nint main(){using namespace signal;assert(valid_frequency(100000)&&valid_frequency(6000000000ULL)&&!valid_frequency(99999));ChannelPlan p;assert(p.add("uhf",433500000));assert(p.add("vhf",145800000));assert(!p.add("vhf",200000));assert(!p.add("bad",1));assert((p.ordered_names()==std::vector<std::string>{"vhf","uhf"}));}')
cmd=["g++","-std=c++17","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g",'frequency.cpp','channel_plan.cpp',"test_student.cpp","-o","student_test"]
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
