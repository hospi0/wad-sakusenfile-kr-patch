# -*- coding: utf-8 -*-
"""파일 안 글꼴 묶음(첫 등장 순) 찾기·문자열 풀기(읽기 전용).  python tools/font_block.py 파일 스테이트 [디스크]"""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS, asc_table
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
fn, st = sys.argv[1], sys.argv[2]
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
rd = lambda n: iso.read(*ent[n][1:3])
mp = rd('/VIEWCG/ASC16MAP.BIN'); cg = rd('/VIEWCG/ASC16X16.BIN') + rd('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
d = rd(fn)
s, v = mstate.load('work/states/%s.state' % st)
o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vr = bytes(b)
# VRAM 의 0xD2 칸부터가 글꼴이라 보고, 파일 안 같은 그림 위치로 시작점을 맞춘다
offs = collections.Counter()
for k in range(1, 400):
    g = vr[(0xD2 + k * 4) * 32:(0xD2 + k * 4) * 32 + 128]
    if len(set(g)) < 6: continue
    q = d.find(g)
    if q >= 0: offs[q - k * 128] += 1
print('시작 후보', [(hex(a), c) for a, c in offs.most_common(4)])
base = offs.most_common(1)[0][0]
L = []; i = 0
while base + (i + 1) * 128 <= len(d):
    g = d[base + i * 128:base + i * 128 + 128]
    c = G.get(g)
    if c is None: c = '?'
    L.append(c); i += 1
    if i > 900: break
    if i > 60 and L[-8:].count('?') == 8: L = L[:-8]; break
print(len(L), ''.join(L)[:900])
n = len(L)
key = struct.pack('>6H', 1, 2, 3, 4, 5, 6)
for m in list(re.finditer(re.escape(key), d))[:5]:
    print('시작 열', hex(m.start()))
un = sum(1 for c in L if c == '?')
print('못 읽음', un)
import pickle
pickle.dump((base, L), open('work/text/fb_%s.pkl' % fn.strip('/').replace('/', '_'), 'wb'))
# 문자열 후보: FFFF 로 끊긴 u16 열 전부 번호 < n
W = struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2]); ff = [i for i, x in enumerate(W) if x == 0xFFFF]
res = []
for a, c in zip(ff, ff[1:]):
    q = W[a + 1:c]
    if 2 <= len(q) <= 200 and all(x < n or x == 0xFFFE for x in q) and sum(1 for x in q if x) >= 2:
        res.append((( a + 1) * 2, ''.join(L[x] if x < n else '/' for x in q)))
print('문자열', len(res)); print(' | '.join(r[1] for r in res)[:2600])
