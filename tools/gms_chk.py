# -*- coding: utf-8 -*-
"""GMS 글꼴 늘리기 검증(읽기 전용): 복사 호출 참조, 뒤 VRAM 비었는지, 번호 상한 코드."""
import sys, os, struct, glob, re
sys.path.insert(0, 'tools')
import asc_build as B, mstate
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); g1 = iso.read(*E['/GMS1.BIN'][1:3]); d = iso.read(*E['/GMS2.BIN'][1:3])
for T in (0xB10, 0xB14, 0xB18, 0xB1C):
    print(hex(T), [hex(i) for i in range(0, T, 2) if struct.unpack_from('>H', g1, i)[0] >> 12 == 0xD and (i & ~3) + 4 + (struct.unpack_from('>H', g1, i)[0] & 255) * 4 == T])
key = d[0xD95C:0xD95C + 64]; ok = []; bad = []
for f in glob.glob('work/states/*.state') + glob.glob('my files/작전파일/*.state*'):
    s, v = mstate.load(f); o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
    if m[0x2020:0x2060] == key:
        (ok if not any(m[0x51A0:0x5E00]) else bad).append(os.path.basename(f))
print('글꼴 올라온 스테이트, 뒤 빔', ok, '안 빔', bad)
