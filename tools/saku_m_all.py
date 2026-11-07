# -*- coding: utf-8 -*-
"""지도 덧그림 전 시나리오 모음(층 합침, 읽기 전용). python tools/saku_m_all.py"""
import sys, os, glob, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
tot = collections.Counter(); out = []
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk()
    ms = sorted((f for f in fs if '/SAKU_M' in f[0] or '/SAK_M' in f[0]), key=lambda f: f[0]); print(tag, len(ms), collections.Counter(f[2] for f in ms).most_common(4))
    for f in ms:
        d = iso.read(f[1], f[2]); n = len(d) // 0x4000
        L = np.frombuffer(d[:n * 0x4000], np.uint8).reshape(n, 128, 128)
        out.append((tag + f[0][-7:-4], L.max(0)))
C = 12; S = 132; R = (len(out) + C - 1) // C
for s in range(0, len(out), 48):
    part = out[s:s + 48]; pg = Image.new('L', (C * S * 1, ((len(part) + C - 1) // C) * S), 40); d = ImageDraw.Draw(pg)
    for i, (n, a) in enumerate(part):
        x, y = i % C * S, i // C * S; pg.paste(Image.fromarray(a), (x, y)); d.text((x + 2, y + 2), n, fill=255)
    pg = pg.resize((pg.width * 1, pg.height * 1), 0); pg.save('work/view/sakum_all_%d.png' % (s // 48))
print(len(out))
