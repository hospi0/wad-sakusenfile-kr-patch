# -*- coding: utf-8 -*-
import sys, struct, re
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import mstate, asc_build as B
s, v = mstate.load('work/states/turn2.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
base = [49, 35, 133, 134, 135]
for off in range(-3, 4):
    q = [x + off for x in base]
    for name, key in (('u16', struct.pack('>5H', *q)), ('u8', bytes(q)), ('u16l', struct.pack('>3H', *q[2:]))):
        for k in ('MAIN/WorkRAML', 'MAIN/WorkRAMH'):
            m = mem(k); h = [hex(x.start()) for x in re.finditer(re.escape(key), m)][:4]
            if h and name != 'u16l': print(off, name, k, h)
# 화면 맵: 턴 글자 칸 값
m = mem('VDP2/VRAM'); W = struct.unpack('>%dH' % (len(m) // 2), m)
iso, E = B.disc('K'); T = iso.read(*E['/TURNASC.BIN'][1:3])
p = m.find(T[128 * 133:128 * 133 + 32]); print('글꼴 VRAM', hex(p), hex(p - 133 * 128), '칸', hex((p - 133 * 128) // 32))
c0 = (p - 133 * 128) // 32
for i in range(0x20000 // 2, len(W) - 1):
    x = W[i] & 0xFFF
    if x == c0 + 133 * 4 and W[i + 1] & 0xFFF == x + 1:
        print(hex(i * 2), ' '.join('%X' % q for q in W[i - 10:i + 10]), [((q & 0xFFF) - c0) / 4 for q in W[i - 6:i + 8:2]])
