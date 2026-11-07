# -*- coding: utf-8 -*-
"""GMS2 전용 글꼴 적재 조사(읽기 전용)."""
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3])
print(len(d), d[0xD940:0xD960].hex(' ')); print('뒤', d[0xD95C + 99 * 128 - 16:0xD95C + 99 * 128 + 48].hex(' '))
c = collections.Counter()
for i in range(0, len(d) - 3, 2):
    x = struct.unpack_from('>I', d, i)[0]
    if 0x200000 <= x < 0x300000 or 0x6000000 <= x < 0x6100000:
        for o in (0xD95C, 0x14A0, 0x11938, 0x11950): c[x - o] += 1
print([(hex(a), n) for a, n in c.most_common(6)])
for b in [a for a, n in c.most_common(6)]:
    t = [(hex(o), [hex(i) for i in range(0, len(d) - 3, 2) if struct.unpack_from('>I', d, i)[0] == o + b][:4]) for o in (0xD95C, 0x10ADC, 0x14A0, 0x11938, 0x1194E, 0x1A60)]
    print(hex(b), t)
for v in (0x3180, 0x18C, 99, 0x63, 0xC60):
    print(hex(v), [hex(i) for i in range(0, 0x1400, 2) if struct.unpack_from('>H', d, i)[0] == v][:8])
