# -*- coding: utf-8 -*-
"""ゲーム・セレクト画面 문자열 찾기(읽기 전용): 글꼴 칸 번호를 글자 그림으로 찾아 전 파일 u16 검색."""
import sys, os, glob, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); E = {f[0]: f for f in iso.walk()}
r = lambda n: iso.read(*E[n][1:3])
mp = r('/VIEWCG/ASC16MAP.BIN'); cg = r('/VIEWCG/ASC16X16.BIN') + r('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
d = r('/GMS2.BIN'); L = [G.get(d[0xD95C + i * 128:0xD95C + i * 128 + 128], '?') for i in range(99)]
print(''.join(L))
W = 'ゲーム'
ids = [[i + 1 for i, c in enumerate(L) if c == x] for x in W]; print(ids)
sel = [[i + 1 for i, c in enumerate(L) if c == x] for x in 'セレクト']; print(sel)
for a in ids[0]:
  for b in ids[1]:
    for c in ids[2]:
      k = struct.pack('>3H', a, b, c)
      for m in re.finditer(re.escape(k), d):
          o = m.start(); q = struct.unpack('>14H', d[o - 2:o + 26]); print(hex(o), q, ''.join(L[v - 1] if 0 < v <= 99 else '.' for v in q))
for c2 in sel[0]:
  for c3 in sel[1]:
    k = struct.pack('>2H', c2, c3)
    for m in re.finditer(re.escape(k), d):
        o = m.start()
        if o % 2 == 0 and o < 0x20000:
            q = struct.unpack('>12H', d[o - 10:o + 14]); print('セレ', hex(o), ''.join(L[v - 1] if 0 < v <= 99 else '.' for v in q))
print()
W2 = struct.unpack('>%dH' % 72, d[0x118E0:0x118E0 + 144])
s = ''
for i, v in enumerate(W2):
    s += '{%X}' % (0x118E0 + i * 2) if i % 8 == 0 else ''
    s += '|' if v == 0xFFFF else ('_' if v == 0 else (L[v - 1] if v <= 99 else '<%X>' % v))
print(s)
