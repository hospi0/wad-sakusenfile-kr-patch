# -*- coding: utf-8 -*-
"""작전 문자열을 작전 시트로 두 배치로 그려 보기(읽기 전용)."""
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
F = B.disc('F'); K = B.disc('K')
def rd(x, n): return x[0].read(*x[1][n][1:3])
mp = rd(F, '/VIEWCG/ASC16MAP.BIN'); w = struct.unpack('>%dH' % (len(mp) // 2), mp)
fa, fb = rd(F, '/VIEWCG/ASC16X16.BIN'), rd(F, '/VIEWCG/ASC16_2.BIN')
kc = rd(K, '/VIEWCG/ASC16X16.BIN') + rd(K, '/VIEWCG/ASC16_2.BIN')
def tile(c, i):
    a = np.zeros((16, 16), np.uint8)
    for q in range(4):
        o = (w[i * 4 + q] - 0x800) * 32; b = np.frombuffer(c[o:o + 32].ljust(32, b'\0'), np.uint8)
        t = np.stack([b >> 4, b & 15], 1).reshape(8, 8); a[q // 2 * 8:q // 2 * 8 + 8, q % 2 * 8:q % 2 * 8 + 8] = t
    return a * 17
d = rd(F, '/00000000.BIN'); rows = []
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t')
    if tag == 'F' and fn in ('/00000000.BIN', '/GAMEOVER.BIN') and fn == '/00000000.BIN':
        o = int(o, 16); n = int(n); q = struct.unpack('>%dH' % n, d[o:o + n * 2])
        if max(q) >= 600: rows.append((i, q))
print(len(rows), rows[:3]); rows = rows[:16]
L = (('concat', fa + fb), ('fixed', fa[:70912] + fb), ('K', kc))
pg = Image.new('L', (3 * 330, len(rows) * 20), 30)
for y, (i, q) in enumerate(rows):
    for x, (nm, c) in enumerate(L):
        for k, v in enumerate(q[:20]):
            if v < 1192: pg.paste(Image.fromarray(tile(c, v)), (x * 330 + k * 16, y * 20))
pg.save('work/view/asc_f.png')
