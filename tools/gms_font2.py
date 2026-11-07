# -*- coding: utf-8 -*-
"""GMS2 적재 주소·글꼴 VRAM 위치(읽기 전용)."""
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, mstate
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3])
s, v = mstate.load('work/states/44.state')
print([k for k in v if 'RAM' in k.upper()][:12])
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
regs = {}
for k in v:
    if k in ('MAIN/WorkRAML', 'MAIN/WorkRAMH', 'VDP1/VRAM', 'VDP2/VRAM'):
        regs[k] = v[k][1]
print(regs)
g = d[0xD95C + 128 * 5:0xD95C + 128 * 5 + 64]; st = d[0x14A0:0x14A0 + 32]
for k in regs:
    for name, m in (('swap', mem(k)), ('raw', s[v[k][0]:v[k][0] + v[k][1]])):
        a = m.find(g); b = m.find(st)
        if a >= 0 or b >= 0: print(k, name, '글꼴', hex(a), '문자열', hex(b))
        for t in range(2):
            c = [m.find(d[0xD95C + 128 * i:0xD95C + 128 * i + 32]) for i in (0, 1, 2, 3, 40, 98)]
            if t == 0 and any(x >= 0 for x in c): print('   칸들', [hex(x) for x in c])
            break
