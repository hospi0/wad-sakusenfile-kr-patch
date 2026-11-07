# -*- coding: utf-8 -*-
"""SAKU_M 지도 파일 구조 보기(읽기 전용). python tools/saku_m.py 번호"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image
n = sys.argv[1]
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/SAKUSEN/SAKU_M%s.BIN' % n][1:3]); print(len(d), d[:32].hex(' '))
a = np.frombuffer(d, np.uint8); W = 128; H = len(d) // W
b = a[:W * H].reshape(H, W)
cols = 7; h = (H + cols - 1) // cols; pg = np.zeros((h, cols * (W + 4)), np.uint8) + 40
for i in range(cols):
    c = b[i * h:(i + 1) * h]; pg[:len(c), i * (W + 4):i * (W + 4) + W] = c
Image.fromarray(pg).resize((pg.shape[1] * 2, pg.shape[0] * 2), 0).save('work/view/sakum_%s.png' % n); print(pg.shape)
