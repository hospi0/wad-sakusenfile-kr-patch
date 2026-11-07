# -*- coding: utf-8 -*-
import sys, struct, re, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, ded_build as D
iso, E = B.disc('K'); G = D.gm(iso, E); T = iso.read(*E['/TURNASC.BIN'][1:3]); d = iso.read(*E['/GAME2.BIN'][1:3])
L = [D.FIXT.get(i, G.get(T[i * 128:i * 128 + 128], '?')) for i in range(188)]
print(d[0x5DC86:0x5DD40].hex(' '))
a = 0x5DC86; s = ''
for i, x in enumerate(d[a:a + 0x180]):
    s += ('|' if x == 0 else (L[x] if x < 188 else '<%X>' % x))
print(s)
idx = D.ptrs(d, 0x217000)
print([(hex(o), [hex(q) for q in idx[o]][:3]) for o in sorted(idx) if 0x5DC86 <= o < 0x5DE80][:30])
