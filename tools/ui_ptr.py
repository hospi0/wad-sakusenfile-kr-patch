# -*- coding: utf-8 -*-
"""UI 문자열 포인터·적재 주소 찾기(읽기 전용).  python tools/ui_ptr.py"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
rows = [l.rstrip('\n').split('\t') for l in open('work/text/ui_pos.tsv', encoding='utf-8')]
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
for fn in ('/GAME2.BIN', '/00000000.BIN', '/GAMEOVER.BIN'):
    offs = sorted({int(r[3], 16) for r in rows if r[2] == fn and r[1] == 'K'})
    if not offs: continue
    d = iso.read(*ent[fn][1:3]); n = len(d) // 4
    best = collections.Counter()
    for al in (0, 2):
        V = np.frombuffer(d[al:al + (len(d) - al) // 4 * 4], '>u4').astype(np.int64)
        V = V[(V >= 0x6004000) & (V < 0x6100000)]
        for o in offs[:200]:
            for b, c in zip(*np.unique(V - o, return_counts=True)):
                if b > 0: best[int(b)] += int(c)
    print(fn, len(d), len(offs), [(hex(b), c) for b, c in best.most_common(6)], flush=True)
    base = best.most_common(1)[0][0]
    S = {o + base: o for o in offs}
    hit = []
    for i in range(0, len(d) - 3, 2):
        v = struct.unpack_from('>I', d, i)[0]
        if v in S: hit.append((i, S[v]))
    print(' 포인터', len(hit), '문자열', len(offs), '가리켜진', len({h[1] for h in hit}), [(hex(a), hex(b)) for a, b in hit[:6]])
    ga = sorted({h[1] for h in hit}); miss = [o for o in offs if o not in set(ga)]
    print(' 안 가리켜진', len(miss), [hex(x) for x in miss[:16]])
