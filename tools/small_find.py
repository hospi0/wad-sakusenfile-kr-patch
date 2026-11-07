# -*- coding: utf-8 -*-
"""반각 낱말 위치 찾기(읽기 전용)."""
import sys, os, glob, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
K8 = {v: k + 1 for k, v in UN.S.items()}
W = ['マジノライン', 'クウテイブタイ', 'リエージュ', 'アーヘン', 'オーディオ', 'サウンドテスト', 'ジコク', 'テキコク', 'エバン']
keys = {w: bytes(K8[c] for c in w) for w in W}
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); h = collections.defaultdict(list)
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP', '.DC')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for w, b in keys.items():
            o = d.find(b)
            if o >= 0: h[w].append((f[0], hex(o)))
    for w in W: print(tag, w, len(h[w]), h[w][:3])
