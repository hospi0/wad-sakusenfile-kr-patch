# -*- coding: utf-8 -*-
"""반각 가나 유닛 이름 찾기(읽기 전용)."""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
keys = ['ﾎﾍｲ', 'ﾊﾘｹｰﾝ', 'ﾎｷｭｳｼｬ', 'ｷｶﾝﾎｳ', 'ﾀｲﾌｰﾝ']
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); c = collections.Counter(); ex = {}
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP', '.DC')) or f[2] < 64 or f[0].startswith('/CDDA'): continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for k in keys:
            b = k.encode('cp932'); n = d.count(b)
            if n: c[f[0]] += n; ex.setdefault(f[0], (k, hex(d.find(b))))
    print(tag, len(c), c.most_common(14), list(ex.items())[:6])
