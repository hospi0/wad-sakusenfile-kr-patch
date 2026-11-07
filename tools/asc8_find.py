# -*- coding: utf-8 -*-
"""작은 글자 유닛 이름 저장 찾기(읽기 전용)."""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
t = [0x7f, 0x54, 0x96, 0x50, 0x5e, 0x95]
keys = {'u8': bytes(t), 'u8-1': bytes(x - 1 for x in t), 'u16': struct.pack('>6H', *t), 'u16-1': struct.pack('>6H', *[x - 1 for x in t])}
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); c = collections.Counter(); ex = {}
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP', '.DC')) or f[2] < 16 or f[0].startswith('/CDDA'): continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for k, b in keys.items():
            n = d.count(b)
            if n: c[(f[0], k)] = n; ex[(f[0], k)] = hex(d.find(b))
    print(tag, len(c), [(k, n, ex[k]) for k, n in c.most_common(12)])
