# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GAME2.BIN'][1:3]); S = T.SHEET
def show(a, n):
    W = struct.unpack('>%dH' % n, d[a:a + n * 2]); return ''.join('|' if x == 0xFFFF else (S[x] if x < len(S) else '<%X>' % x) for x in W)
idx = {}
for i in range(0, len(d) - 3, 2): idx.setdefault(struct.unpack_from('>I', d, i)[0], []).append(i)
for o in (0x1D3F4, 0x1FEB6, 0x1FEC0):
    print(hex(o), show(o - 32, 40))
    for k in range(0, 64, 2):
        h = idx.get(o - k + 0x217000)
        if h: print('  -%d' % k, [hex(x) for x in h][:5])
print(d[0x1D3D0:0x1D410].hex(' '))
