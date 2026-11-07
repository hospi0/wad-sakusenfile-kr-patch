# -*- coding: utf-8 -*-
"""GMS 화면에서 비어 있고 참조 안 되는 칸 범위 찾기(읽기 전용)."""
import sys, struct, collections, glob, os
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, mstate, sh2dis
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3]); g1 = iso.read(*E['/GMS1.BIN'][1:3])
key = d[0xD95C + 128 * 90:0xD95C + 128 * 90 + 32]
ref = set(); nz = set(); used = []
fs = ['5', '6', '25', '26', '44']
for n in fs:
    s, v = mstate.load('work/states/%s.state' % n); o, c = v['VDP2/VRAM']; b = bytearray(s[o:o + c]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
    W = struct.unpack('>%dH' % (len(m) // 2), m)
    for i in range(0x20000 // 2, 0x50000 // 2):
        ref.add(W[i] & 0xFFF); ref.add(W[i] & 0x7FFF)
    for c_ in range(0, 0x4000):
        if any(m[c_ * 32:c_ * 32 + 32]): nz.add(c_)
print('칸 최대 비어 있지 않음', hex(max(x for x in nz if x < 0x1000)))
run = []; st = None
for c_ in range(0x28D, 0x1000):
    ok = c_ not in nz and c_ not in ref
    if ok and st is None: st = c_
    if not ok and st is not None:
        if c_ - st >= 16: run.append((hex(st), c_ - st, hex(st * 32)))
        st = None
print(run[:14])
c = collections.Counter(x for x in ref if 0x28D <= x < 0x1000); print(len(c))
print('0x1AA8 쓰임'); 
for i in range(0, 0x38D4, 2):
    w = struct.unpack_from('>H', g1, i)[0]
    if w >> 12 == 0xD and (i & ~3) + 4 + (w & 255) * 4 == 0x38D4: sh2dis.dump(g1, i - 6, 12, 0x6060400)
