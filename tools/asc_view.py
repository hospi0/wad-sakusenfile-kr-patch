# -*- coding: utf-8 -*-
"""VIEWCG 글자 시트 보기(읽기 전용).  python tools/asc_view.py"""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
iso = Iso(glob.glob(glob.glob(B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin')[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
print([(f[0], f[2]) for f in fs if f[0].startswith('/VIEWCG/') and f[2]])
for n in ('ASC16X16', 'ASC16_2', 'ASC8X8'):
    f = ent['/VIEWCG/%s.BIN' % n]; d = iso.read(f[1], f[2]); print(n, len(d), d[:32].hex(' '))
    b = d[32:]; cells = len(b) // 32; W = 64; H = (cells + W - 1) // W; im = np.zeros((H * 8, W * 8), np.uint8)
    for i in range(cells):
        a = np.frombuffer(b[i * 32:i * 32 + 32], np.uint8); p = np.stack([a >> 4, a & 15], 1).reshape(8, 8)
        im[i // W * 8:i // W * 8 + 8, i % W * 8:i % W * 8 + 8] = p * 17
    s = 2 if H * 8 < 500 else 1
    Image.fromarray(im).resize((W * 8 * 2, H * 8 * 2), 0).save('work/view/%s.png' % n); print(H * 8)
