# -*- coding: utf-8 -*-
"""작전파일 병기 타입 선택 메뉴(GMS2 0x31A40, 176×142, 8비트) 한글화.  python tools/f_type.py 폴더"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, mstate, bdf
import numpy as np
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
G14 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri11.bdf')
iso, E = B.disc('F'); g = iso.read(*E['/GMS2.BIN'][1:3]); O = 0x31A40
a = np.frombuffer(g[O:O + 176 * 142], np.uint8).reshape(142, 176).copy(); src = a.copy()
s, v = mstate.load('work/states_sf/1.state'); co, cn = v['VDP2/CRAM']; cr = np.frombuffer(bytes(s[co:co + cn]), '<u2').astype(int)
def rgb(x, b):
    c = cr[(x.astype(int) + b) & 0x7FF]; return np.stack([(c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3], 2).astype(np.uint8)
S = np.vstack([np.hstack([rgb(src, b * 0x100) for b in range(i, i + 4)]) for i in (0, 4)])
Image.fromarray(S).save(OUT + '/banks.png'); print(S.shape)
print('줄 0', src[20, 40:60].tolist(), '행별 고유', [len(set(src[y, 44:168].tolist())) for y in range(0, 142, 8)])
b = 0x200
col = src[:, 100]; print('열 100', col.tolist())
L = lambda i: (lambda c: (c & 31) * 3 + (c >> 5 & 31) * 6 + (c >> 10 & 31))(int(cr[(int(i) + b) & 0x7FF]))
def glyphs(t):
    pts, _ = G14.draw(t); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    m = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1), bool)
    for x, y in pts: m[y - min(ys), x - min(xs)] = True
    return m
bands = []; y = 0
rowmode = [int(np.bincount(src[r, 48:170]).argmax()) for r in range(142)]
print('줄 최빈 밝기', [L(v) for v in rowmode])
BANDS = [(int(a_), int(b_)) for a_, b_ in zip(sys.argv[2].split(',')[0::2], sys.argv[2].split(',')[1::2])] if len(sys.argv) > 2 else []
TX = ['독일 타입', '일본 타입', '미국 타입', '소련 타입', '영국 타입']
for (y0, y1), t in zip(BANDS, TX):
    sub = a[y0:y1, 43:160]; bg = np.array([np.bincount(sub[r]).argmax() for r in range(sub.shape[0])])
    Lv = np.vectorize(L)(sub); ink = int(sub.flat[Lv.argmin()]); hi = int(sub.flat[Lv.argmax()])
    for r in range(sub.shape[0]): sub[r, :] = bg[r]
    m = glyphs(t); h, w = m.shape; cx, cy = (117 - w) // 2, (y1 - y0 - h) // 2
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx] and cy + yy + 1 < sub.shape[0] and cx + xx + 1 < sub.shape[1]:
                sub[cy + yy + 1, cx + xx + 1] = hi
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx]: sub[cy + yy, cx + xx] = ink
if BANDS:
    open(OUT + '/GMS2_31A40.bin', 'wb').write(a.tobytes())
    Image.fromarray(np.hstack([rgb(src, b), rgb(a, b)])).resize((352 * 3, 142 * 3), 0).save(OUT + '/미리보기_타입메뉴_왼쪽원본_오른쪽한글.png')
