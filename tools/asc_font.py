# -*- coding: utf-8 -*-
"""ASC16MAP+ASC16X16 글자 복원, 화면 글자 번호 판정, 문자열 저장 찾기(읽기 전용).  python tools/asc_font.py"""
import sys, os, glob, re, struct, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
rd = lambda n: iso.read(*ent[n][1:3])
mp = rd('/VIEWCG/ASC16MAP.BIN'); cg = rd('/VIEWCG/ASC16X16.BIN'); c2 = rd('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); N = len(w) // 4
print('글자', N, min(w), max(w), len(cg) // 32, len(c2) // 32)
s, v = mstate.load('work/states/7.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP2/VRAM')
# 화면 글자 그림
m = np.frombuffer(vr[0x7C000:0x7E000], '>u2').reshape(64, 64).astype(int)
seq = [(3, x) for x in (16, 18, 20, 22, 24)] + [(7, 10), (7, 12), (7, 16), (11, 10), (11, 12)]
scr = []
for y, x in seq:
    t = m[y, x] & 0xFFF; scr.append(vr[t * 32:t * 32 + 128])
base = min(w)
for name, src, b0 in (('X16', cg, 0x800), ('X16-0', cg, 0), ('A2', c2, 0)):
    G = {}
    for i in range(N):
        q = w[i * 4:i * 4 + 4]; g = b''.join(src[(t - b0) * 32:(t - b0) * 32 + 32] for t in q)
        G.setdefault(g, i)
    print(name, [G.get(g, -1) for g in scr])
c2g = {c2[i:i + 128]: i // 128 for i in range(0, len(c2), 128)}; print('A2 직접', [c2g.get(g, -1) for g in scr])
c2g = {c2[32 + i:32 + i + 128]: i // 128 for i in range(0, len(c2) - 32, 128)}; print('A2 +32', [c2g.get(g, -1) for g in scr])

print('=== 문자열')
keys = [struct.pack('>HHH', 125, 284, 436), struct.pack('>HH', 280, 281), struct.pack('>HH', 167, 168), struct.pack('<HHH', 125, 284, 436)]
c = collections.Counter(); ex = {}
for f in fs:
    if f[0].endswith(('.MUS', '.CPK', '/')) or f[2] < 64 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    for i, k in enumerate(keys):
        n = d.count(k)
        if n: c[(f[0], i)] = n; ex[(f[0], i)] = hex(d.find(k))
print(c.most_common(16)); print({k: ex[k] for k, _ in c.most_common(8)})
