# -*- coding: utf-8 -*-
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, mstate
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3])
for x in (0x20D95C, 0x20D8DC, 0x210ADC, 0x25A02020, 0x25E02020, 0x25E02000, 0x25E01FA0, 0x2020, 0x3180, 0x3200):
    r = [hex(i) for i in range(0, min(len(d), 0x90000) - 3, 2) if struct.unpack_from('>I', d, i)[0] == x]; print(hex(x), r[:6])
g2 = iso.read(*E['/GAME2.BIN'][1:3])
print('code', len(d), d[:32].hex(' '))
s, v = mstate.load('work/states/44.state')
o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
print('VRAM 뒤', m[0x51A0:0x51E0].hex(' ')); 
nz = [i for i in range(0x51A0, 0x8000, 32) if any(m[i:i + 32])]; print('채워진 칸', len(nz), hex(nz[0]) if nz else '', hex(nz[-1]) if nz else '')
print('앞', m[0x1F80:0x2020].hex(' ')[:200])
