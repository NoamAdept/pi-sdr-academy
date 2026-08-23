#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

Path("test_student.cpp").write_text('#include "radio.hpp"\n#include <cassert>\nint main(){const Radio first("desk",100);assert(first.name()=="desk"&&first.frequency()==100);Radio r("roof",50);assert(!r.tune(0)&&r.frequency()==50);assert(r.tune(145800000)&&r.frequency()==145800000);}')
cmd=["g++","-std=c++17","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g",'radio.cpp',"test_student.cpp","-o","student_test"]
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
