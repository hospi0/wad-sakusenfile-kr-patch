# -*- coding: utf-8 -*-
import sys, struct, glob, re, os
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import ded_build as D, asc_build as B, mstate
iso, E = B.disc('K'); d = iso.read(*E['/RMC2.BIN'][1:3]); r1 = iso.read(*E['/RMC1.BIN'][1:3]); print(len(d), len(r1))
G = D.gm(iso, E); L = [G.get(d[0x44 + i * 128:0x44 + i * 128 + 128], '?').replace('□', '?') for i in range(88)]
L = ['面' if c == '?' and i == 41 else c for i, c in enumerate(L)]; L = [c.replace('?', 'よ') if i == 20 else c for i, c in enumerate(L)]
print(''.join(L)); o = 0x2EF4; s = ''
while True:
    x = struct.unpack_from('>H', d, o)[0]; o += 2
    if x == 0xFFFF: break
    s += '/' if x == 0xFFFE else ('　' if x == 0 else (L[x - 1] if x <= 88 else '#'))
print(s, hex(o)); print(d[o:o + 48].hex(' ')); print('처음', d[:0x44].hex(' '))
hit = {}
for f in glob.glob('work/states/*.state'):
    s_, v = mstate.load(f)
    for k in ('MAIN/WorkRAML', 'MAIN/WorkRAMH'):
        a, n = v[k]; b = bytearray(s_[a:a + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; p = bytes(b).find(d[0x2C48:0x2C80])
        if p >= 0: hit.setdefault((k, hex(p)), []).append(os.path.basename(f))
print({k: v[:3] for k, v in hit.items()})
for nm, c in (('RMC1', r1), ('RMC2', d)):
    print(nm, [(hex(i), hex(struct.unpack_from('>I', c, i)[0])) for i in range(0, len(c) - 3, 2) if (struct.unpack_from('>I', c, i)[0] & 0xFFFF) in (0x2C48, 0x2C9A, 0x2CB8, 0x2D8C, 0x2DF0, 0x2E16, 0x2EF4)][:12])
print('---')
o = 0x2EF4
while o < 0x3400:
    st = o; s = ''
    while True:
        x = struct.unpack_from('>H', d, o)[0]; o += 2
        if x == 0xFFFF: break
        s += '/' if x == 0xFFFE else ('　' if x == 0 else (L[x - 1] if x <= 88 else '#'))
        if o - st > 600: break
    pp = [hex(i) for i in range(0, len(r1) - 3, 2) if struct.unpack_from('>I', r1, i)[0] == 0x200000 + st]
    print(hex(st), (o - st) // 2 - 1, pp, s)
