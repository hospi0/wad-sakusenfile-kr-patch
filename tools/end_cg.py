# -*- coding: utf-8 -*-
"""VIEWCG 결과 그림 보기(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
ns = ['A_END', 'G_END', 'J_END', 'STHIKI', 'STKACHI', 'STMAKE']
pg = Image.new('RGB', (3 * 356, 2 * 228)); d = ImageDraw.Draw(pg)
for i, n in enumerate(ns):
    b = iso.read(*ent['/VIEWCG/%s.BIN' % n][1:3]); a = np.frombuffer(b, '>u2')[:352 * 224]
    im = np.stack([(a & 31) << 3, (a >> 5 & 31) << 3, (a >> 10 & 31) << 3], 1).reshape(224, 352, 3).astype(np.uint8)
    x, y = i % 3 * 356, i // 3 * 228; pg.paste(Image.fromarray(im), (x, y)); d.text((x + 2, y + 2), n, fill=(255, 255, 0))
pg.save('work/view/end_cg.png')
