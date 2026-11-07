# -*- coding: utf-8 -*-
"""GAME2.BIN 글꼴 후보 그려 보기(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0])
ent = {f[0]: f for f in iso.walk()}
d = iso.read(ent['/GAME2.BIN'][1], ent['/GAME2.BIN'][2]); print(len(d))
o = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x70000
# 바이트 폭별 통 그림
pg = Image.new('L', (1500, 900), 40); x = 4
for wb in (1, 2, 3, 4, 8, 16):
    a = np.unpackbits(np.frombuffer(d[o:o + 24000], np.uint8))
    h = min(880, len(a) // (wb * 8))
    im = Image.fromarray((a[:h * wb * 8].reshape(h, wb * 8) * 255).astype(np.uint8))
    S = max(1, 2 if wb <= 4 else 1)
    im = im.resize((im.width * S, im.height * S), 0).crop((0, 0, im.width * S, 880)); pg.paste(im, (x, 4)); x += im.width + 12
pg.save('work/view/g2.png')
