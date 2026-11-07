# -*- coding: utf-8 -*-
"""시험본과 원본 파일별 차이(읽기 전용)."""
import sys, os, glob, collections, hashlib
sys.path.insert(0, 'tools')
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
o = sorted(glob.glob(glob.glob(SS.B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin'))[0]; n = glob.glob('work/disc/*Koutetsu*Track 1*.bin')[0]
a = Iso(o); b = Iso(n); c = collections.Counter(); ch = []
for f in a.walk():
    if f[0].startswith('/CDDA') or f[2] == 0: continue
    try: x = a.read(f[1], f[2]); y = b.read(f[1], f[2])
    except EOFError: continue
    if x != y: ch.append(f[0]); c[os.path.dirname(f[0]) or '/'] += 1
print(len(ch), c.most_common()); print([x for x in ch if not x.endswith(('.EP',)) and 'SAKU_' not in x])
print(os.path.getsize(o) == os.path.getsize(n), hashlib.md5(open(n, 'rb').read()).hexdigest())
