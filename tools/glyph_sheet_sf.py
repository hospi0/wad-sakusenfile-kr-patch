# -*- coding: utf-8 -*-
"""고유 글자 판독 대조 시트(빈도순).  python tools/glyph_sheet.py"""
import sys, os, glob, struct, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
R2 = glob.glob(B + r'\*Sakusen*')[0]
iso = Iso(sorted(glob.glob(R2 + r'\*.bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
G = {}
for f in sorted(fs):
    if '/SAK_F' in f[0]:
        b = iso.read(f[1], f[2])
        for i in range(0, len(b), 128): G.setdefault(hashlib.md5(b[i:i + 128]).hexdigest()[:10], b[i:i + 128])
rows = [l.rstrip('\n').split('\t') for l in open('work/text/glyph_sf.tsv', encoding='utf-8')]
def px(g):
    a = np.frombuffer(g, np.uint8); p = np.stack([a >> 4, a & 15], 1).reshape(4, 8, 8)
    o = np.zeros((16, 16), np.uint8); o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = p; return o
order = sorted(range(len(rows)), key=lambda i: rows[i][1])
T = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 20); N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 11)
W = 22; per = 22 * 13; CW, CH = 62, 78
for s in range(0, len(order), per):
    pg = Image.new('RGB', (W * CW, 13 * CH), (30, 30, 40)); d = ImageDraw.Draw(pg)
    for j, i in enumerate(order[s:s + per]):
        x, y = j % W * CW, j // W * CH
        im = Image.fromarray((px(G[rows[i][0]]) * 17).astype(np.uint8)).resize((48, 48), 0).convert('RGB'); pg.paste(im, (x + 2, y + 2))
        d.text((x + 2, y + 51), rows[i][1], font=T, fill=(255, 220, 90)); d.text((x + 26, y + 58), str(i), font=N, fill=(150, 220, 255))
    pg.save('work/view/sfgs_%d.png' % (s // per))
print(len(order))
