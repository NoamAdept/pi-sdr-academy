#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

cmd=["gcc","-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g","list.c","test_student.c","-o","student_test"] + ''.split()
Path("test_student.c").write_text('#include "list.h"\n#include <assert.h>\nint main(void){struct node*h=0;assert(list_length(h)==0);assert(list_push_front(&h,4));assert(list_push_front(&h,9));assert(list_length(h)==2);assert(h->value==9&&h->next->value==4);assert(list_find(h,4)==h->next);assert(list_find(h,8)==0);list_destroy(&h);assert(h==0);return 0;}')
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
