# -*- coding: utf-8 -*-
"""GMS2 96×24 4비트 판 묶음 보기(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/GMS2.BIN'][1:3]); a0 = 0x1EF26 - 1152 * 26; n = 60
pg = Image.new('L', (6 * 208, 10 * 66), 30); dr = ImageDraw.Draw(pg)
for i in range(n):
    o = a0 + i * 1152; x = np.frombuffer(d[o:o + 1152], np.uint8); q = (np.stack([x >> 4, x & 15], 1).reshape(24, 96) * 17).astype(np.uint8)
    X, Y = i % 6 * 208, i // 6 * 66; pg.paste(Image.fromarray(q).resize((192, 48), 0), (X + 2, Y + 14)); dr.text((X + 2, Y + 2), hex(o), fill=255)
pg.save('work/view/gms_plates.png'); print(hex(a0))
