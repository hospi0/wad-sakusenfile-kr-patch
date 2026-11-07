# -*- coding: utf-8 -*-
"""ASC16 번호로 된 큰 유닛 이름 찾기(읽기 전용)."""
import sys, struct, re, collections, os
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, asc_table as T
S = T.SHEET
iso, E = B.disc('K')
def idx(c): return [i for i, x in enumerate(S) if x == c]
keys = []
for w in ('大司令', '司令部', '歩兵'):
    import itertools
    for t in itertools.product(*[idx(c) for c in w]): keys.append((w, struct.pack('>%dH' % len(t), *t)))
print(idx('大'), idx('司'), idx('令'), idx('部'), idx('歩'), idx('兵'))
h = collections.Counter(); ex = {}
for f in iso.walk():
    if f[2] < 8 or f[0].startswith('/CDDA') or f[0].endswith(('.MUS', '.CPK', '.EP', '.DC')) or 'SAKU_M' in f[0]: continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    for w, k in keys:
        for m in re.finditer(re.escape(k), d):
            if m.start() % 2 == 0: h[(f[0], w)] += 1; ex.setdefault((f[0], w), hex(m.start()))
print(h.most_common(20)); print(list(ex.items())[:10])
