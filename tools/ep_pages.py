# -*- coding: utf-8 -*-
"""엔딩 EP 판 크게 보기(왼쪽 판만, 읽기 전용). python tools/ep_pages.py"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
eps = sorted((f for f in iso.walk() if f[0].endswith('.EP')), key=lambda f: f[0])
tiles = []
for f in eps:
    b = iso.read(f[1], f[2]); a = np.frombuffer(b, '>u2').reshape(336, 704)
    for k in range(3):
        c = a[k * 112:(k + 1) * 112, 352:704]
        im = np.stack([(c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3], 2).astype(np.uint8)
        tiles.append((f[0][1:-3], k, Image.fromarray(im)))
R = 6
for s in range(0, len(tiles), 3 * R):
    pg = Image.new('RGB', (3 * 480, R * 156), (0, 0, 0)); d = ImageDraw.Draw(pg)
    for i, (n, k, im) in enumerate(tiles[s:s + 3 * R]):
        x, y = i % 3 * 480, i // 3 * 156; pg.paste(im.resize((476, 152), Image.NEAREST), (x, y)); d.rectangle((x, y, x + 70, y + 11), fill=(0, 0, 0)); d.text((x + 2, y), n, fill=(255, 255, 0))
    pg.save('work/view/ep_p%d.png' % (s // (3 * R)))
print(len(tiles))
