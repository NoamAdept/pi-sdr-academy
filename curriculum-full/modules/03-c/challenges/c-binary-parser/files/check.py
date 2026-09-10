#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

cmd=["gcc","-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g","records.c","test_student.c","-o","student_test"] + ''.split()
Path("test_student.c").write_text('#include "records.h"\n#include <assert.h>\nstruct state{int calls;int total;};\nstatic void see(uint8_t t,const uint8_t*p,size_t n,void*c){struct state*s=c;s->calls++;s->total+=t+(int)n+(n?p[0]:0);}\nint main(void){uint8_t d[]={1,2,9,8,4,0};struct state s={0};assert(parse_records(d,6,see,&s));assert(s.calls==2&&s.total==16);uint8_t bad[]={2,4,1};assert(!parse_records(bad,3,see,&s));assert(parse_records(d,0,see,&s));return 0;}')
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
