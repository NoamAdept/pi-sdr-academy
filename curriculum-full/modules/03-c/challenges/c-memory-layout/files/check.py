#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

cmd=["gcc","-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g","layout.c","test_student.c","-o","student_test"] + ''.split()
Path("test_student.c").write_text('#include "layout.h"\n#include <assert.h>\nint main(void){uint8_t d[]={ \'R\',\'X\',0x34,0x12,0xa5,9};struct header h;assert(decode_header(d,6,&h));assert(h.tag[0]==\'R\'&&h.tag[1]==\'X\'&&h.sequence==0x1234&&h.flags==0xa5&&h.length==9);assert(!decode_header(d,5,&h));assert(!decode_header(0,6,&h));return 0;}')
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
