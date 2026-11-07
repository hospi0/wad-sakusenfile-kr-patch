# -*- coding: utf-8 -*-
"""TURNASC·RMC2 문자열 구조 보기(읽기 전용)."""
import sys, os, re, struct, collections, io, contextlib
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, gms_build as G
iso, E = B.disc('K'); r = lambda n: iso.read(*E[n][1:3])
src = open('tools/extract2.py', encoding='utf-8').read()
fixT = eval(re.search(r"font\(T, 0, 188, (\{.*?\})\)", src).group(1))
mp = r('/VIEWCG/ASC16MAP.BIN'); cg = r('/VIEWCG/ASC16X16.BIN') + r('/VIEWCG/ASC16_2.BIN'); import asc_table
w = struct.unpack('>%dH' % (len(mp) // 2), mp); Gm = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); Gm.setdefault(g, asc_table.SHEET[i])
T = r('/TURNASC.BIN'); L = [fixT.get(i, Gm.get(T[i * 128:i * 128 + 128], '?')) for i in range(188)]
print(''.join(L)); print('빈 칸', [i for i in range(188) if not any(T[i * 128:i * 128 + 128])])
d = r('/GAME2.BIN'); base = 0x217000
idx = collections.defaultdict(list)
for i in range(0, len(d) - 3, 2):
    x = struct.unpack_from('>I', d, i)[0] - base
    if 0 <= x < len(d): idx[x].append(i)
o = 0x5D7C0; n = 0
while o < 0x5DEC0:
    st = o; s = ''
    while True:
        x = struct.unpack_from('>H', d, o)[0]; o += 2
        if x == 0xFFFF: break
        s += '/' if x == 0xFFFE else (L[x] if x < 188 else '<%X>' % x)
        if o - st > 300: break
    print(hex(st), (o - st) // 2 - 1, [hex(q) for q in idx.get(st, [])][:3], s[:70])
