# -*- coding: utf-8 -*-
"""스테이트 CPU 상태와 램 대조(읽기 전용). python tools/st_cpu.py 파일"""
import sys, os, struct, glob
sys.path.insert(0, 'tools')
import mstate, sh2dis, asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])
ks = [k for k in v if k.startswith('SH2-M/') and any(t in k for t in ('.PC', '.R', 'PC', 'SR', 'PR', 'VBR', 'GBR', 'MACH'))]
print(ks[:24])
for k in ks[:24]:
    o, n = v[k]; b = s[o:o + n]
    print(k, n, b[:80].hex(' ') if n <= 80 else b[:64].hex(' '))
print([k for k in v if k.startswith('SH2-M/') and len(k) < 14][:40])
def le32(k):
    o, n = v[k]; return [struct.unpack_from('<I', s, o + i)[0] for i in range(0, n, 4)]
for k in ('SH2-M/R', 'SH2-M/CtrlRegs', 'SH2-M/SysRegs', 'SH2-M/GBR', 'SH2-M/VBR', 'SH2-M/SR', 'SH2-M/PR'):
    if k in v: print(k, [hex(x) for x in le32(k)])
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
H = mem('MAIN/WorkRAMH'); Lo = mem('MAIN/WorkRAML')
print('PC 주변'); sh2dis.dump(H, 0x940, 28, 0x6000000)
regs = le32('SH2-M/R') if 'SH2-M/R' in v else []
if regs:
    sp = regs[15]; print('SP', hex(sp))
    if 0x6000000 <= sp < 0x6100000: print('스택', [hex(struct.unpack_from('>I', H, sp - 0x6000000 + i)[0]) for i in range(0, 64, 4)])
iso, E = B.disc('K')
for fn in ('/GMS2.BIN', '/GAME2.BIN', '/00000000.BIN', '/GMS1.BIN'):
    d = iso.read(*E[fn][1:3])
    print(fn, 'L', Lo.find(d[0x400:0x440]), 'H', H.find(d[0x400:0x440]))
