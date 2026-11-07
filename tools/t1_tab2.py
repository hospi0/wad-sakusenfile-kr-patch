# -*- coding: utf-8 -*-
import sys, struct, re, collections, glob
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, mstate
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3]); g1 = iso.read(*E['/GMS1.BIN'][1:3]); c0 = iso.read(*E['/00000000.BIN'][1:3])
T = 0x1AAC
print('표 앞', ' '.join('%X' % x for x in struct.unpack('>12H', d[T - 16:T + 8])))
print('표 끝', ' '.join('%X' % x for x in struct.unpack('>120H', d[T + 98 * 8:T + 98 * 8 + 240])))
for a in (T, T - 8, T + 8, 0x1A60, 0x1A62, 0x1A70, 0x1AA0, 0x1AA4, 0x1AA8):
    for nm, f in (('GMS1', g1), ('0000', c0), ('GMS2', d[:0x1400])):
        h = [hex(m.start()) for m in re.finditer(re.escape(struct.pack('>I', 0x200000 + a)), f)]
        if h: print(hex(a), nm, h[:5])
s, v = mstate.load('work/states/t1.state'); o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
W = struct.unpack('>%dH' % (len(m) // 2), m)
# 맵 페이지 후보 0x28000 / 그 밖: 값이 0x28D~0x3FF 인 곳
c = collections.Counter()
for i in range(0x20000 // 2, len(W)):
    x = W[i] & 0xFFF
    if 0x28D <= x <= 0x3FF: c[(i * 2) & ~0x1FFF] += 1
print('참조 페이지', [(hex(k), n) for k, n in c.most_common(12)])
