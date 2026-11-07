# -*- coding: utf-8 -*-
"""작은 글자(8×8) 면 번호 읽기(읽기 전용). python tools/asc8_map.py 스테이트"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP2/VRAM')
for m in (0x7E000, 0x7C000, 0x34000, 0x1E000):
    a = np.frombuffer(vr[m:m + 0x2000], '>u2').reshape(64, 64).astype(int)
    sm = (a & 0xFFF)
    for y in range(64):
        xs = [x for x in range(64) if 0 < sm[y, x] < 0xD2]
        if len(xs) >= 3: print(hex(m), y, [(x, hex(int(a[y, x]))) for x in xs[:14]])
