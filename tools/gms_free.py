# -*- coding: utf-8 -*-
import sys, os, re
sys.path.insert(0, 'tools')
import asc_build as B, mstate
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3]); print(hex(len(d)), hex(E['/GMS2.BIN'][1]))
R = sorted(((m.end() - m.start(), m.start()) for m in re.finditer(rb'\0{2048,}', d)), reverse=True)[:8]
s, v = mstate.load('work/states/44.state')
o, n = v['MAIN/WorkRAML']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
for L, a in R: print(hex(a), hex(L), '스테이트 44 램도 0?', not any(m[a:a + L]))
print('파일 뒤 램', m[len(d):len(d) + 32].hex(' '), '끝까지 0?', not any(m[len(d):]), hex(len(m)))
nz = [i for i in range(len(d), len(m), 4096) if any(m[i:i + 4096])]; print([hex(x) for x in nz[:12]], len(nz))
print('다음 파일 시작 LBA', sorted((f[1], f[0]) for f in iso.walk() if f[1] > E['/GMS2.BIN'][1])[:2], (len(d) + 2047) // 2048)
