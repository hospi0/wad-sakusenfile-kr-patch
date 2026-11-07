# -*- coding: utf-8 -*-
"""DAI_*.DC(16비트 그림)와 SAKU_F*.BIN 판독(읽기 전용).  python tools/dc_view.py"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0])
ent = {f[0]: f for f in iso.walk()}
os.makedirs('work/view', exist_ok=True)

def rgb(d, w):
    a = np.frombuffer(d[:len(d) // (2 * w) * 2 * w], '>u2').reshape(-1, w).astype(np.uint32)
    r = (a & 31) << 3; g = (a >> 5 & 31) << 3; b = (a >> 10 & 31) << 3
    return Image.fromarray(np.stack([r, g, b], 2).astype(np.uint8))

names = [f for f in ent if f.endswith('.DC')]
print(names)
ims = [(f, rgb(iso.read(ent[f][1], ent[f][2]), 352)) for f in sorted(names)]
pg = Image.new('RGB', (4 * 356, 3 * 240), (40, 40, 40)); d = ImageDraw.Draw(pg)
for i, (f, im) in enumerate(ims[:12]):
    pg.paste(im, ((i % 4) * 356, (i // 4) * 240 + 14)); d.text(((i % 4) * 356 + 2, (i // 4) * 240 + 1), f, fill=(255, 255, 0))
pg.save('work/view/dc.png')

def bpp4(d, w):
    a = np.frombuffer(d, np.uint8); p = np.stack([a >> 4, a & 15], 1).reshape(-1)
    return p[:len(p) // w * w].reshape(-1, w)

for f in ('/SAKUSEN/SAKU_F01.BIN',):
    d = iso.read(ent[f][1], ent[f][2]); print(f, len(d), [hex(x) for x in sorted(set(d))[:20]], (np.frombuffer(d, np.uint8) != 0).mean())
    pg = Image.new('L', (1500, 1000), 30); x = 0; y = 0
    for w in (256, 280, 288, 304, 320, 352, 384, 448):
        a = bpp4(d, w); im = Image.fromarray((a * 17).astype(np.uint8))
        if y + im.height > 1000: y = 0; x += 500
        pg.paste(im.crop((0, 0, min(w, 460), min(im.height, 330))), (x, y)); y += min(im.height, 330) + 4
    pg.save('work/view/saku_f01.png')
