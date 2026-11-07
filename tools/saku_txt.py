# -*- coding: utf-8 -*-
"""지도 글자 화소 값 파악 + 글자층만 크게 모음(읽기 전용). python tools/saku_txt.py"""
import sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
out = []
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk()
    for f in sorted((f for f in fs if '/SAKU_M' in f[0] or '/SAK_M' in f[0]), key=lambda f: f[0]):
        d = iso.read(f[1], f[2]); n = len(d) // 0x4000
        out.append((tag + f[0][-7:-4], np.frombuffer(d[:n * 0x4000], np.uint8).reshape(n, 128, 128)))
L = out[0][1]
for i in range(7): print(i, collections.Counter(int(v) for v in L[i].ravel() if v).most_common(6))
if len(sys.argv) > 1:
    v = [int(x) for x in sys.argv[1].split(',')]
    C = 7; S = 262
    for s in range(0, len(out), 21):
        part = out[s:s + 21]; pg = Image.new('L', (C * S, ((len(part) + C - 1) // C) * S), 30); dr = ImageDraw.Draw(pg)
        for i, (n, a) in enumerate(part):
            m = np.isin(a, v).any(0); im = Image.fromarray((m * 255).astype(np.uint8)).resize((256, 256), 0)
            x, y = i % C * S, i // C * S; pg.paste(im, (x, y)); dr.text((x + 2, y + 2), n, fill=200)
        pg.save('work/view/mtxt_%d.png' % (s // 21))
