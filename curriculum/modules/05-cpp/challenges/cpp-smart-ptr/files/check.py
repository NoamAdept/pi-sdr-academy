#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

Path("test_student.cpp").write_text('#include "node.hpp"\n#include <cassert>\nint main(){Node root("root");Node*a=root.add_child("a");a->add_child("leaf");root.add_child("b");assert(root.child_count()==2);assert(root.find("leaf")->name()=="leaf");assert(root.find("none")==nullptr);const Node&c=root;assert(c.find("b")!=nullptr);}')
cmd=["g++","-std=c++17","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g",'node.cpp',"test_student.cpp","-o","student_test"]
r=subprocess.run(cmd,text=True,capture_output=True)
if r.returncode: fail("compile failed:\n"+r.stderr)
r=subprocess.run(["./student_test"],text=True,capture_output=True,env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1"})
if r.returncode: fail("tests failed:\n"+r.stdout+r.stderr)

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
