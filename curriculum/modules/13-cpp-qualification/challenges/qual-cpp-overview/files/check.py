#!/usr/bin/env python3
from pathlib import Path
import os
def fail(m):
    print('Not yet:', m); raise SystemExit(1)
p=Path('answer.txt')
if not p.is_file(): fail('create answer.txt')
got=p.read_text(encoding='utf-8').strip().splitlines()[0].strip()
if got != 'cpp-qualification': fail(f'expected cpp-qualification, got '+got)
fp=Path(Path('.flagpath').read_text().strip()) if Path('.flagpath').exists() else Path(os.environ.get('ACADEMY_FLAG_PATH','/home/flag.txt'))
fp.parent.mkdir(parents=True, exist_ok=True); fp.write_text(''); print('CHECK_OK')
