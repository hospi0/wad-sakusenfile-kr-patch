# -*- coding: utf-8 -*-
"""지도 층 글자(색 108)를 ASC8X8 글자와 대조해 위치·문자열 찾기(읽기 전용).  python tools/map_ocr.py"""
import sys, os, glob, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/VIEWCG/ASC8X8.BIN'][1:3])
T = {}
for i in range(1, 0x9F):
    a = np.frombuffer(d[i * 32:i * 32 + 32], np.uint8); q = np.stack([a >> 4, a & 15], 1).reshape(8, 8) > 0
    c = UN.S.get(i)
    if c and q.sum() > 3: T[c] = q
print('글자', len(T))


def scan(L):
    m = L == 108; H, W = m.shape; hits = []
    ys, xs = np.nonzero(m)
    if len(ys) == 0: return []
    for y in range(max(0, ys.min() - 8), min(H - 7, ys.max() + 1)):
        for x in range(0, W - 7):
            b = m[y:y + 8, x:x + 8]; n = b.sum()
            if n < 4: continue
            best = None; bs = 0
            for c, q in T.items():
                s = (b & q).sum() * 2 / (n + q.sum())
                if s > bs: best, bs = c, s
            if bs >= 0.8: hits.append((y, x, best, bs))
    return hits


if __name__ == '__main__':
    f = ent['/SAKUSEN/SAKU_M01.BIN']; D = iso.read(f[1], f[2]); L = np.frombuffer(D[3 * 0x4000:4 * 0x4000], np.uint8).reshape(128, 128)
    h = scan(L); print(len(h), sorted(h, key=lambda x: -x[3])[:30])
    m = L == 108
    for y in range(0, 128):
        if m[y].any(): print('%3d' % y, ''.join('#' if v else '.' for v in m[y]))
