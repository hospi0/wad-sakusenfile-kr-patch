# -*- coding: utf-8 -*-
"""VDP2 레지스터로 면 배치 판독(읽기 전용).  python tools/vdp2reg.py 스테이트"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])
rr = [k for k in v if 'RawRegs' in k or 'Regs' in k and 'VDP2' in k]; print(rr[:6])
a, c = v[rr[0]]; r = [int(x) for x in np.frombuffer(s[a:a + c], '<u2')]
R = lambda o: r[o // 2]
print('TVMD %04X BGON %04X CHCTLA %04X CHCTLB %04X BMPNA %04X PNCN0-3 %04X %04X %04X %04X PLSZ %04X MPOFN %04X' % (R(0), R(0x20), R(0x28), R(0x2A), R(0x2C), R(0x30), R(0x32), R(0x34), R(0x36), R(0x3A), R(0x3C)))
print('MPABN0 %04X MPCDN0 %04X MPABN1 %04X MPCDN1 %04X MPABN2 %04X MPABN3 %04X' % (R(0x40), R(0x42), R(0x44), R(0x46), R(0x48), R(0x4C)))
print('PRINA %04X PRINB %04X' % (R(0xF8), R(0xFA)))
