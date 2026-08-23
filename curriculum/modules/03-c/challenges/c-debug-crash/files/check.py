#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

cmd=["gcc","-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g","crash.c","test_student.c","-o","student_test"] + ''.split()
Path("test_student.c").write_text('#include "crash.h"\n#include <assert.h>\nint main(void){int a[]={-2,10,20};assert(average_positive(a,3)==15.0);int b[]={-2,0};assert(average_positive(b,2)==0.0);assert(average_positive(0,0)==0.0);return 0;}')
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
