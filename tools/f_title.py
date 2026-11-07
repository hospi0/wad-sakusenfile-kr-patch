# -*- coding: utf-8 -*-
"""작전파일 제목 띠(DAI_TIT1 0x200, 312×28, 16비트) 한글화.  python tools/f_title.py 폴더 → 폴더/F_DAI_TIT1.bin, preview.png"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
import numpy as np
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FD = r'C:\claude\utils\font'; BH = glob.glob(FD + r'\blackhansans\*.ttf')[0]
iso, E = B.disc('F'); d = iso.read(*E['/DAI_TIT1.DC'][1:3])
a = np.frombuffer(d[0x200:0x200 + 312 * 28 * 2], '>u2').reshape(28, 312)
rgb = np.stack([(a & 31) << 3, (a >> 5 & 31) << 3, (a >> 10 & 31) << 3], 2).astype(np.float32); msb = a & 0x8000
r, g = rgb[..., 0], rgb[..., 1]
m = np.zeros((28, 312), bool); m[:, 80:232] = (r[:, 80:232] < 110) | (g[:, 80:232] < r[:, 80:232] * 0.45)
def dil(m, n):
    m = m.copy()
    for _ in range(n):
        q = m.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): q |= np.roll(np.roll(m, dy, 0), dx, 1)
        m = q
    return m
m = dil(m, 1)
# 줄무늬 철판: 같은 줄을 주기만큼 옮겨 복사 + 밝기 맞춤
best = (1e12, 0)
for per in range(8, 64):
    x0, x1 = 10, 70
    e = np.abs(rgb[:, x0:x1] - rgb[:, x0 + per:x1 + per]).mean()
    if e < best[0]: best = (e, per)
per = best[1]; print('주기', per)
new = rgb.copy()
for y in range(28):
    for x in range(312):
        if not m[y, x]: continue
        for k in range(1, 12):
            hit = None
            for sgn in (-1, 1):
                q = x + sgn * per * k
                if 0 <= q < 312 and not m[y, q]: hit = q; break
            if hit is not None: new[y, x] = rgb[y, hit]; break
# 밝기: 원본 흐름(저주파)을 넓은 평균으로 맞춤
from PIL import ImageFilter
F_ = ImageFont.truetype(BH, 28)
im = Image.fromarray(np.clip(new, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
dr.text((158, 16), '작전 파일', (120, 80, 8), font=F_, anchor='mm')
dr.text((157, 15), '작전 파일', (40, 12, 4), font=F_, anchor='mm')
n = np.asarray(im, np.float32); R = np.clip(n, 0, 255).astype(np.uint16) >> 3
open(OUT + '/F_DAI_TIT1.bin', 'wb').write((msb | R[:, :, 0] | R[:, :, 1] << 5 | R[:, :, 2] << 10).astype('>u2').tobytes())
o = Image.new('RGB', (312 * 3, 28 * 3 * 2 + 8), (30, 30, 40))
o.paste(Image.fromarray(rgb.astype(np.uint8)).resize((312 * 3, 84), 0), (0, 0)); o.paste(im.resize((312 * 3, 84), 0), (0, 92)); o.save(OUT + '/미리보기_작전파일_제목_위원본_아래새것.png')
