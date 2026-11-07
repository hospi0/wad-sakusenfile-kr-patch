# -*- coding: utf-8 -*-
"""파일 구간을 폭 W 로 펼쳐 보기(읽기 전용). python tools/raster.py 파일 시작 끝 폭 bits 이름 [디스크 K|F]"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image
fn, a, b, W, bits, nm = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
p = glob.glob(SS.B + (r'\*Sakusen*' if len(sys.argv) > 7 and sys.argv[7] == 'F' else r'\*Koutetsu*'))[0]
iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent[fn][1:3])[a:b]
x = np.frombuffer(d, np.uint8)
px = (np.stack([x >> 4, x & 15], 1).reshape(-1) * 17).astype(np.uint8) if bits == 4 else x
H = 980; per = W * H; n = (len(px) + per - 1) // per
pg = np.zeros((H, n * (W + 4)), np.uint8) + 40
for i in range(n):
    c = px[i * per:(i + 1) * per]; c = np.pad(c, (0, per - len(c))).reshape(H, W); pg[:, i * (W + 4):i * (W + 4) + W] = c
Image.fromarray(pg).save('work/view/%s.png' % nm); print(pg.shape)
