# -*- coding: utf-8 -*-
"""화면 글자(ASC16) 맵 번호와 저장 형식 찾기(읽기 전용).  python tools/asc_map.py 스테이트"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP2/VRAM')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
iso = Iso(glob.glob(glob.glob(B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin')[0]); ent = {f[0]: f for f in iso.walk()}
for n in ('ASC16X16', 'ASC16_2', 'ASC8X8'):
    f = ent['/VIEWCG/%s.BIN' % n]; d = iso.read(f[1], f[2])
    hits = []
    for o in range(0, len(d) - 64, 32):
        t = d[o:o + 64]
        if len(set(t)) < 8: continue
        p = vr.find(t)
        if p >= 0: hits.append((o, p, p - o))
    c = collections.Counter(h[2] for h in hits); print(n, len(d), '일치 칸', len(hits), [(hex(a), b) for a, b in c.most_common(4)])
m = v and None
# 맵 후보: u16 배열에서 0 아닌 값이 많은 곳
w = np.frombuffer(vr, '>u2')
for base in range(0, len(w), 0x800):
    blk = w[base:base + 0x800]; nz = np.count_nonzero(blk)
    if nz > 30: print(hex(base * 2), nz, [hex(int(x)) for x in blk[blk > 0][:14]])

print('=== 2워드 맵')
base = 0x1A40 // 32
for m0 in range(0x20000, 0x40000, 0x2000):
    a = np.frombuffer(vr[m0:m0 + 0x2000], '>u2').reshape(-1, 2)
    t = a[:, 1].astype(int)
    idx = np.nonzero((t >= base) & (t < base + 0x8A0))[0]
    if len(idx) > 8:
        print(hex(m0), len(idx), [(int(i) % 64, int(i) // 64, hex(int(a[i, 0])), hex(int(t[i]))) for i in idx[:16]])
print('=== 1워드 맵')
for m0 in range(0x14000, 0x80000, 0x1000):
    a = np.frombuffer(vr[m0:m0 + 0x1000], '>u2').astype(int)
    c = a & 0x3FF
    idx = np.nonzero(((a & 0xFFF) >= base) & ((a & 0xFFF) < base + 0x8A0))[0]
    if len(idx) > 60: print(hex(m0), len(idx), [hex(int(x)) for x in a[idx[:12]]])
for k in ('VDP2/RawRegs', 'VDP2/RAWRegs'):
    if k in v: print(k, s[v[k][0]:v[k][0] + 0x80].hex(' '))
print([k for k in v if k.startswith('VDP2')][:40])
