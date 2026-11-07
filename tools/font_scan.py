# -*- coding: utf-8 -*-
"""글꼴 후보 찾기(읽기 전용): 전 파일 구간을 16×16 1bpp·4bpp 로 보아 글자 모양 점수.  python tools/font_scan.py"""
import sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0])
fs = [f for f in iso.walk() if not f[0].endswith(('.CPK', '.MUS', '.EP')) and not f[0].endswith('/') and not f[0].startswith(('/UNIT3D', '/VIEWMAP', '/EARTH', '/VIEWCG')) and f[2] > 4000]
res = []
for f in fs:
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    for bs in range(0, len(d) - 8192, 8192):
        c = d[bs:bs + 8192]
        a = np.unpackbits(np.frombuffer(c, np.uint8))
        den = a.mean()
        if not 0.12 < den < 0.42: continue
        for row, nm in ((16, '1bpp16'), (12, '1bpp12'), (24, '1bpp24'), (8, '1bpp8')):
            m = (a[:-row] & a[row:]).sum() / max(1, a.sum())       # 위아래 줄 일치
            r = (a[:-1] & a[1:]).sum() / max(1, a.sum())            # 옆 화소 일치
            res.append((round(float(m + r), 3), nm, f[0], bs, round(float(den), 2)))
res.sort(reverse=True)
seen = collections.Counter(); out = []
for x in res:
    if seen[x[2]] < 2: out.append(x); seen[x[2]] += 1
for x in out[:16]: print(x)
os.makedirs('work/view', exist_ok=True)
sizes = {f[0]: f for f in fs}
print(sorted(((f[2], f[0]) for f in fs if f[0].count('/') == 1 and f[2] < 200000), reverse=True)[:30])
