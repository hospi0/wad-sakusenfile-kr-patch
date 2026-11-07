# -*- coding: utf-8 -*-
"""턴 시작 화면 글자 칸 값(면 값 전체)이 RAM 에 그대로 있나(읽기 전용)."""
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load('work/states/7.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP2/VRAM')
row = vr[0x7C000 + 7 * 128:0x7C000 + 8 * 128]; print(row[40:80].hex(' '))
g = vr[0x29A * 32:0x29A * 32 + 128]
for nm in ('MAIN/WorkRAML', 'MAIN/WorkRAMH'):
    b = mem(nm)
    for name, key in (('글자 그림', g), ('줄', row[48:56]), ('칸값', struct.pack('>H', 0xB29A))):
        ps = [m.start() for m in re.finditer(re.escape(key), b)]
        print(nm, name, len(ps), [hex(x) for x in ps[:6]])
