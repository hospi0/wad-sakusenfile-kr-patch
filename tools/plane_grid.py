# -*- coding: utf-8 -*-
"""면을 칸 눈금·좌표와 함께 크게 그림(읽기 전용).  python tools/plane_grid.py 스테이트 면 x0 y0 x1 y1 → work/view/audit/g_<스테이트>_<면>.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
from PIL import Image, ImageDraw
st, p, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:7])
s, v = mstate.load('work/states/%s.state' % st)
o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vr = bytes(b)
a, c = v['VDP2/RawRegs']; r = [int(x) for x in np.frombuffer(s[a:a + c], '<u2')]
R = lambda x: r[x // 2]
mp = {0: R(0x40) & 0x3F, 1: R(0x44) & 0x3F, 2: R(0x48) & 0x3F, 3: R(0x4C) & 0x3F}[p]
base = (R(0x30 + p * 2) >> 2 & 7) << 12
m = np.frombuffer(vr[mp * 0x2000:mp * 0x2000 + 0x2000], '>u2').reshape(64, 64)
k = 'VDP2/CRAM' if 'VDP2/CRAM' in v else max((x for x in v if 'CRAM' in x), key=lambda x: v[x][1])
co, cn = v[k]; cb = bytearray(s[co:co + cn]); cb[0::2], cb[1::2] = cb[1::2], cb[0::2]; cr = np.frombuffer(bytes(cb), '>u2').astype(int)
cao = {0: R(0xE4) & 7, 1: R(0xE4) >> 4 & 7, 2: R(0xE4) >> 8 & 7, 3: R(0xE4) >> 12 & 7}[p]
S = 4; W = (x1 - x0) * 8; H = (y1 - y0) * 8
g = np.zeros((H, W), int)
for y in range(y0, y1):
    for x in range(x0, x1):
        t = (int(m[y, x]) & 0xFFF) + base
        g[(y - y0) * 8:(y - y0) * 8 + 8, (x - x0) * 8:(x - x0) * 8 + 8] = np.frombuffer(vr[t * 32:t * 32 + 64], np.uint8).reshape(8, 8)
cv = cr[(g + (cao << 8)) & 0x7FF]
rgb = np.stack([(cv & 31) << 3, (cv >> 5 & 31) << 3, (cv >> 10 & 31) << 3], 2).astype(np.uint8)
im = Image.fromarray(rgb).resize((W * S, H * S), 0).convert('RGB'); d = ImageDraw.Draw(im)
for x in range(x0, x1):
    d.line([((x - x0) * 8 * S, 0), ((x - x0) * 8 * S, H * S)], fill=(255, 255, 0) if x % 5 == 0 else (90, 90, 0))
    if x % 5 == 0: d.text(((x - x0) * 8 * S + 2, 1), str(x), fill=(0, 255, 255))
for y in range(y0, y1):
    d.line([(0, (y - y0) * 8 * S), (W * S, (y - y0) * 8 * S)], fill=(255, 255, 0) if y % 5 == 0 else (90, 90, 0))
    if y % 5 == 0: d.text((1, (y - y0) * 8 * S + 1), str(y), fill=(0, 255, 255))
im.save('work/view/audit/g_%s_%d.png' % (st, p)); print(im.size, 'CAOS', cao)
