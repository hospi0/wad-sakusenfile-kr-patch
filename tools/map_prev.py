# -*- coding: utf-8 -*-
"""지도 층별 시험본: 실제 지도 배경 위에 한 층씩(읽기 전용).  python tools/map_prev.py 빌드폴더 출력폴더"""
import sys, os, struct, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
from PIL import Image, ImageDraw
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
s, v = mstate.load('work/states/28.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vram = mem('VDP1/VRAM'); cram = np.frombuffer(mem('VDP2/CRAM'), '>u2').astype(int)
p = 0; seen = set(); sp = []
for _ in range(4000):
    if p in seen or p + 32 > len(vram): break
    seen.add(p); c = struct.unpack_from('>16H', vram, p); ctrl, link, mode, col, src, size = c[0:6]; jp = ctrl >> 12 & 7
    if ctrl & 0x8000: break
    if not ctrl & 0x4000 and (ctrl & 15) in (0, 1, 2): sp.append(((size >> 8) * 8, size & 255, mode >> 3 & 7, col, src * 8))
    p = link * 8 if jp in (1, 2) else p + 32
print([x for x in sp if x[0] >= 96])
big = [x for x in sp if x[0] >= 128 and x[1] >= 128]
def rgb(a, bank):
    q = cram[(a.astype(int) + bank) & 0x7FF]
    return np.stack([(q & 31) << 3, (q >> 5 & 31) << 3, (q >> 10 & 31) << 3], 2).astype(np.uint8)
bg = None; ovbank = 0
for w, h, m, col, src in big:
    a = np.frombuffer(vram[src:src + w * h], np.uint8).reshape(h, w)
    if (a == 0).mean() < 0.2 and bg is None: bg = rgb(a, col & 0xFF00); bw = w
    elif (a == 0).mean() >= 0.2: ovbank = col & 0xFF00
print('배경', None if bg is None else bg.shape, hex(ovbank))
base = bg[(bg.shape[0] - 128) // 2:, (bg.shape[1] - 128) // 2:][:128, :128]
names = ['K_SAKU_M01', 'K_SAKU_M08', 'K_SAKU_M13', 'K_SAKU_M24', 'K_SAKU_M26', 'F_SAK_M171']
S = 3; tiles = []
for n in names:
    f = '%s/%s.bin' % (SRC, n)
    if not os.path.exists(f): print('없음', n); continue
    L = np.fromfile(f, np.uint8).reshape(-1, 128, 128)
    ls = [i for i in range(len(L)) if (L[i] == 108).sum() > 30]
    for i in ls[:3]:
        o = base.copy(); m = L[i] != 0; c = rgb(L[i], ovbank); o[m] = c[m]; tiles.append(('%s 층%d' % (n[-6:], i), o))
C = 4; R = (len(tiles) + C - 1) // C; pg = Image.new('RGB', (C * (128 * S + 6), R * (128 * S + 18)), (30, 30, 30)); d = ImageDraw.Draw(pg)
for i, (t, o) in enumerate(tiles):
    x, y = i % C * (128 * S + 6), i // C * (128 * S + 18); d.text((x + 2, y + 2), t, fill=(255, 255, 0)); pg.paste(Image.fromarray(o).resize((128 * S, 128 * S), 0), (x, y + 14))
pg.save(OUT + '/layers.png'); print(pg.size, len(tiles))
