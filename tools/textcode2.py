# -*- coding: utf-8 -*-
"""SAKU_F 글자 번호열로 문장 저장 위치 찾기(읽기 전용).  python tools/textcode2.py 스테이트"""
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
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
F = iso.read(*ent['/SAKUSEN/SAKU_F01.BIN'][1:3])
G = {F[i * 128:(i + 1) * 128]: i for i in range(len(F) // 128)}
m = np.frombuffer(vr[0x1E000:0x1E000 + 0x2000], '>u2').reshape(-1, 64)
seq = []
for y in (0, 2, 4):
    for x in range(0, 64, 2):
        t = int(m[y, x]) & 0xFFF
        if not m[y, x]: continue
        seq.append(G.get(vr[t * 32:t * 32 + 128], -1))
print('번호열', seq)
print('맵 칸 → 번호 기준', [(hex(int(m[0, x]) & 0xFFF), seq[x // 2]) for x in range(0, 12, 2)])
good = [x for x in seq if x >= 0][:12]
rel = np.diff(good)
res = collections.Counter()

def scan(name, d):
    for w, dt in ((1, np.uint8), (2, '>u2'), (2, '<u2')):
        for off in range(w):
            a = np.frombuffer(d[off:off + (len(d) - off) // w * w], dt).astype(np.int32)
            if len(a) < 16: continue
            df = np.diff(a); hit = np.ones(len(df) - len(rel) + 1, bool)
            for i, r in enumerate(rel[:8]): hit &= df[i:len(df) - len(rel) + 1 + i] == r
            for p in np.nonzero(hit)[0][:3]:
                print(name, 'bytes' if w == 1 else str(dt), hex(int(p) * w + off), '첫 값', hex(int(a[p])), '번호 차', int(a[p]) - good[0], d[max(0, p * w + off - 16):p * w + off + 40].hex(' '))

for f in fs:
    if f[0].endswith(('.MUS', '.CPK')) or f[2] < 32 or f[0].endswith('/'): continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    scan(f[0], d)
scan('WorkRAMH', wh); scan('WorkRAML', wl)
