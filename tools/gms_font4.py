# -*- coding: utf-8 -*-
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K')
K = [(x, struct.pack('>I', x)) for x in (0x20D95C, 0x20D8DC, 0xD95C, 0xD8DC, 0x25E02020, 0x25E01FA0, 0x25E02000, 0x3180, 0x3200)]
for fn in ('/GMS2.BIN', '/00000000.BIN', '/GAME2.BIN', '/0.BIN', '/GAME1.BIN', '/GMS1.BIN'):
    if fn not in E: continue
    d = iso.read(*E[fn][1:3])
    for x, b in K:
        h = [hex(m.start()) for m in re.finditer(re.escape(b), d) if m.start() % 2 == 0][:6]
        if h: print(fn, hex(x), h)
print(sorted(E)[:40])
