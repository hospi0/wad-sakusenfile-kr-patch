# -*- coding: utf-8 -*-
"""파일 전체에서 글꼴 묶음 자동 찾기 + 그 번호로 된 문자열 찾기(읽기 전용).  python tools/font_block2.py K|F 파일…"""
import sys, os, glob, struct, re, collections, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
tag = sys.argv[1]
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
for g, c in list(G.items()):
    if c == '□': del G[g]
p = glob.glob(SS.B + (r'\*Koutetsu*' if tag == 'K' else r'\*Sakusen*'))[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
for fn in sys.argv[2:]:
    d = iso.read(*ent[fn][1:3]); blocks = []
    for al in range(0, 128, 2):
        i = al; run = 0; start = None; miss = 0; L = []
        while i + 128 <= len(d):
            c = G.get(d[i:i + 128])
            if c:
                if start is None: start = i; L = []
                L.append(c); miss = 0
            elif start is not None:
                miss += 1; L.append('?')
                if miss > 6:
                    if len(L) >= 24: blocks.append((start, L[:-miss]))
                    start = None; miss = 0
            i += 128
    blocks.sort(key=lambda b: -len(b[1]))
    print(fn, len(d), [(hex(b[0]), len(b[1])) for b in blocks[:5]])
    for st, L in blocks[:4]:
        print(hex(st), ''.join(L)[:300])
    pickle.dump(blocks[:4], open('work/text/fb2_%s_%s.pkl' % (tag, fn.strip('/').replace('/', '_')), 'wb'))
