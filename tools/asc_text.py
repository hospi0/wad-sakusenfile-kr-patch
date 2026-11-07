# -*- coding: utf-8 -*-
"""NBG0/1 글자 면 번호 읽기(읽기 전용).  python tools/asc_text.py 스테이트"""
import sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP2/VRAM')
for m in (0x7C000, 0x7E000):
    a = np.frombuffer(vr[m:m + 0x2000], '>u2').reshape(64, 64).astype(int)
    nz = np.argwhere(a); print(hex(m), len(nz), a[a > 0][:20])
    rows = sorted({int(y) for y, x in nz}); print(rows[:30])
    for y in rows[:16]:
        print(y, [(int(x), hex(int(a[y, x]))) for x in np.nonzero(a[y])[0][:14]])
wh = mem('MAIN/WorkRAMH'); wl = mem('MAIN/WorkRAML')
a = np.frombuffer(vr[0x7C000:0x7E000], '>u2').astype(int)
print('맵 고유', len(set(a[a > 0])))
