# -*- coding: utf-8 -*-
"""스테이트 한 장의 스프라이트 전부 모아 보기(읽기 전용). python tools/st_spr.py 44"""
import sys, os, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
import numpy as np
from PIL import Image, ImageDraw
st = sys.argv[1]
sp = SS.sprites('work/states/%s.state' % st)
pg = Image.new('L', (1500, 900), 40); d = ImageDraw.Draw(pg); x = y = 4; hh = 0; seen = set()
for a, w, h, bits, b in sp:
    k = (w, h, b[:64])
    if k in seen or w * h < 200: continue
    seen.add(k)
    if bits == 4:
        t = np.frombuffer(b, np.uint8); p = (np.stack([t >> 4, t & 15], 1).reshape(-1) * 17).astype(np.uint8)
    elif bits == 8: p = np.frombuffer(b, np.uint8)
    else:
        t = np.frombuffer(b, '>u2'); p = ((t >> 5 & 31) << 3).astype(np.uint8)
    im = Image.fromarray(p[:w * h].reshape(h, w))
    if x + w + 6 > 1500: x = 4; y += hh + 18; hh = 0
    d.text((x, y), '%dx%d %X' % (w, h, a), fill=255); pg.paste(im, (x, y + 12)); x += max(w, 60) + 6; hh = max(hh, h)
pg.save('work/view/st_%s.png' % st); print(len(seen))
