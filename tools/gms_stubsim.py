# -*- coding: utf-8 -*-
"""GMS 스텁 시뮬레이터(이 스텁에 쓰는 명령만). 표·지우기·복사 호출 결과를 검산."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')
import gms_build as G
out, bad = G.patch(lambda *a: None); d = out['/GMS2.BIN']; P = G.patch
mem = {}; R = [0] * 16; R[15] = 0x6100000; pc = G.STUB; calls = []; zeroed = {}; n = 0
def rd32(a): return struct.unpack_from('>I', d, a - 0x200000)[0]
R[6] = 0x210ADC; pc = 0x200000 + G.STUB
mem32 = {0x210ADC: 0x31A0}
while True:
    w = struct.unpack_from('>H', d, pc - 0x200000)[0]; n += 1; assert n < 100000
    op = w >> 12; nx = pc + 2
    if op == 0xD: R[w >> 8 & 15] = rd32((pc & ~3) + 4 + (w & 255) * 4)
    elif w == 0x6662: R[6] = mem32[R[6]]
    elif w == 0x400B: calls.append((hex(R[4]), hex(R[5]), R[6], hex(R[0])))
    elif w == 0x0009: pass
    elif w == 0xE300: R[3] = 0
    elif w == 0x2131: mem[R[1]] = R[3] & 0xFFFF
    elif w == 0x7102: R[1] += 2
    elif w == 0x7301: R[3] += 1
    elif w == 0x4210: R[2] -= 1; T = R[2] == 0
    elif w >> 8 == 0x8B:
        if not T: nx = pc + 4 + (struct.unpack('b', bytes([w & 255]))[0]) * 2
    elif w in (0x4F22, 0x4F26): pass
    elif w == 0x000B: break
    else: raise SystemExit('모르는 명령 %04X' % w)
    pc = nx
print('스텁', P.stub, 'B 명령 수행', n); [print(' 호출', c) for c in calls]
tb = [mem.get(0x202F8000 + 0x0 + i * 2) for i in range(len(P.tb))]
print('표 일치', tb == P.tb, len(tb), 'n=1', tb[4:8], 'n=100', tb[400:404], hex(tb[-1]))
for a, b in ((G.Z1, G.Z1END), (G.ZEND2, G.Z2END)):
    print('지움', hex(a), all(mem.get(0x20200000 + x) == 0 for x in range(a, b, 2)))
print('번호표', struct.unpack_from('>13H', d, 0x14DE), '첫 맵', struct.unpack_from('>10H', d, 0x14DE + 26))
print('글자 구역', [(hex(a), hex(b), c) for a, b, c in P.zones], '넘침', bad)
