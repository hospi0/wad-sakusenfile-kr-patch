# -*- coding: utf-8 -*-
import sys, struct, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import mstate, gms_build as G, asc_build as B
st = sys.argv[1] if len(sys.argv) > 1 else 'work/states/t1.state'
s, v = mstate.load(st); o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
W = struct.unpack('>%dH' % (len(m) // 2), m)
hits = collections.Counter()
for stride in (64, 128):
    rows = collections.defaultdict(list)
    for i in range(0, len(W) - stride - 1):
        x = W[i] & 0xFFF
        if x >= 0x100 and W[i + 1] & 0xFFF == x + 1 and W[i + stride] & 0xFFF == x + 2 and W[i + stride + 1] & 0xFFF == x + 3 and W[i] >> 12 == W[i + 1] >> 12:
            rows[i // stride].append((i * 2, hex(W[i]), (x - 0x101) / 4 + 1))
    print('폭', stride, {hex(k * stride * 2): v[:12] for k, v in list(rows.items())[:8]})
print('0x51A0 부근', m[0x5180:0x51C0].hex(' ')); print('뒤 칸 채움', [hex(i) for i in range(0x4F00, 0x6000, 0x80) if any(m[i:i + 0x80])][:40])
for r in (0, 1, 2, 3, 4, 5, 6, 7, 26, 27, 28):
    a = 0x28000 + r * 128; print(hex(a), ' '.join('%X' % x for x in W[a // 2:a // 2 + 46]))
