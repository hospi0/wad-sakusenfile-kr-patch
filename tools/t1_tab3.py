# -*- coding: utf-8 -*-
import sys, struct, re, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, sh2dis
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3]); g1 = iso.read(*E['/GMS1.BIN'][1:3]); c0 = iso.read(*E['/00000000.BIN'][1:3])
for nm, f in (('GMS1', g1), ('0000', c0)):
    h = []
    for i in range(0, len(f) - 3, 2):
        x = struct.unpack_from('>I', f, i)[0]
        if 0x201000 <= x < 0x20D93C: h.append((hex(i), hex(x - 0x200000)))
    print(nm, h[:40])
W = struct.unpack('>%dH' % ((0x3000 - 0x1DCC) // 2), d[0x1DCC:0x3000])
print(' '.join('%X' % x for x in W[:20]))
i = 0; runs = []
while i + 1 < len(W):
    if not (W[i] == 0x30 and W[i + 1] >> 12 == 2): runs.append((hex(0x1DCC + i * 2), hex(W[i]), hex(W[i + 1]))); i += 2; 
    else: i += 2
print(len(runs), runs[:10])
