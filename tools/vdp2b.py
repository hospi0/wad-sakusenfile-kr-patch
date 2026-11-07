# -*- coding: utf-8 -*-
"""글꼴 출처·맵 번호열·문장 코드 찾기(읽기 전용).  python tools/vdp2b.py 스테이트"""
import sys, os, re, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])

def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)

vr = mem('VDP2/VRAM'); wh = mem('MAIN/WorkRAMH'); wl = mem('MAIN/WorkRAML')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk()
keys = [vr[o:o + 64] for o in (0x1000, 0x2400, 0x3000, 0x5000, 0x7000)]
print('키 비었나', [len(set(k)) for k in keys])
for f in fs:
    if f[0].endswith(('.MUS',)) or f[2] < 64 or f[0].endswith('/'): continue
    try: d = iso.read(f[1], min(f[2], 2000000))
    except EOFError: continue
    h = [d.find(k) for k in keys]
    if any(x >= 0 for x in h): print('글꼴 출처', f[0], f[2], [hex(x) for x in h])
for nm, m in (('WorkRAMH', wh), ('WorkRAML', wl)):
    h = [m.find(k) for k in keys]; print(nm, [hex(x) for x in h])
# 맵 후보: 넓은 구간에서 u16 값이 글꼴 칸 범위인 영역
for base in (0x1C000, 0x48000, 0x60000, 0x7C000, 0xC000, 0x8000):
    a = np.frombuffer(vr[base:base + 0x4000], '>u2'); nz = np.nonzero(a)[0]
    if len(nz): print(hex(base), '첫 위치', hex(base + 2 * int(nz[0])), [hex(int(x)) for x in a[nz[:40]]])
