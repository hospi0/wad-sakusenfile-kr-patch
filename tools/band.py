# -*- coding: utf-8 -*-
import sys, struct, re, glob
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, mstate, sh2dis
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3]); g1 = iso.read(*E['/GMS1.BIN'][1:3]); c0 = iso.read(*E['/00000000.BIN'][1:3])
# 원본 띠 스프라이트가 VDP1 VRAM 어디, 파일 어디
s, v = mstate.load('work/states/44.state'); o, n = v['VDP1/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
seg = d[0x19A06 + 0x700:0x19A06 + 0x740]; p = m.find(seg); print('VDP1 위치', hex(p), '시작', hex(p - (0x19A06 + 0x700 - 0x199A6)))
base = p - (0x19A06 + 0x700 - 0x199A6)
print('앞뒤 일치 범위')
a = 0x19A06 + 0x700
q = 0
while m[p - q - 1] == d[a - q - 1] and q < 0x40000: q += 1
r = 0
while m[p + r] == d[a + r] and r < 0x40000: r += 1
print(hex(a - q), hex(a + r), hex(q + r))
for lo, hi in ((a - q - 8, a - q + 8), (a + r - 8, a + r + 8)): pass
# 큰 덩어리 복사: 0x2xxxxx → 0x25C?
for nm, f in (('GMS1', g1), ('0000', c0)):
    print(nm, [(hex(i), hex(struct.unpack_from('>I', f, i)[0])) for i in range(0, len(f) - 3, 2) if (struct.unpack_from('>I', f, i)[0] >> 16) in (0x25C0, 0x25C1, 0x25C2, 0x25C3, 0x25C4, 0x25C5, 0x25C6, 0x25C7)][:20])
print('GMS1 0x8E0 뒤'); sh2dis.dump(g1, 0x8EC, 40, 0x6060400)
print('GMS1 풀', [(hex(i), hex(struct.unpack_from('>I', g1, i)[0])) for i in range(0xB20, 0xBA0, 4)])
