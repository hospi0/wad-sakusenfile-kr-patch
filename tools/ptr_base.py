# -*- coding: utf-8 -*-
"""문자열 참조 포인터 찾기(읽기 전용): 적재 기준값 추정 뒤 넘치는 줄 참조 수."""
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
pos = B.load()
for tag, fn, bases in (('K', '/GAME2.BIN', None), ('K', '/GAMEOVER.BIN', None), ('F', '/GAME2.BIN', None), ('F', '/00000000.BIN', None)):
    iso, E = B.disc(tag); d = iso.read(*E[fn][1:3]); os_ = sorted({r[0] for r in pos[(tag, fn)]})
    L = [struct.unpack_from('>I', d, i)[0] for i in range(0, len(d) - 3, 2)]
    S = set(os_); c = collections.Counter()
    vals = [x for x in L if 0x200000 <= x < 0x300000 or 0x6000000 <= x < 0x6100000]
    for x in set(vals):
        for o in os_: c[x - o] += 1
    top = [(hex(b), n) for b, n in c.most_common(4)]; print(tag, fn, len(d), '줄', len(os_), top)
    b = c.most_common(1)[0][0]
    idx = collections.defaultdict(list)
    for i, x in enumerate(L): idx[x].append(i * 2)
    for o in (0x1D3F4, 0x1FEB6, 0x1FEC0, 0x606CA, 0x7B384, 0x7B3AC, 0xDFA, 0xE20, 0xE42, 0x1EE54, 0x21916, 0x21920, 0x6449A, 0x7F20C, 0x7F234, 0x1F826):
        if o in S: print('  ', hex(o), '참조', [hex(q) for q in idx.get(o + b, [])][:6])
