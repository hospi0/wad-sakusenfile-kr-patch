# -*- coding: utf-8 -*-
"""턴 글꼴 번호로 된 나라 이름 찾기(읽기 전용)."""
import sys, struct, re
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, ded_build as D
iso, E = B.disc('K'); G = D.gm(iso, E); T = iso.read(*E['/TURNASC.BIN'][1:3]); N = 188
L = [D.FIXT.get(i, G.get(T[i * 128:i * 128 + 128], '?')) for i in range(N)]
ix = lambda c: [i for i, x in enumerate(L) if x == c]
print(''.join(L)[:190]); print({c: ix(c) for c in 'ドイツ帝国'})
for fn in ('/GAME2.BIN', '/00000000.BIN', '/GMS2.BIN', '/SHINARIO.BIN'):
    if fn not in E: continue
    d = iso.read(*E[fn][1:3])
    for a in ix('帝'):
        for b in ix('国'):
            for m in re.finditer(re.escape(struct.pack('>2H', a, b)), d):
                o = m.start()
                if o % 2 == 0:
                    w = struct.unpack('>24H', d[o - 24:o + 24]); print(fn, hex(o), ' '.join('%X' % x for x in w[6:18]), ''.join(L[x] if x < N else '.' for x in w))
