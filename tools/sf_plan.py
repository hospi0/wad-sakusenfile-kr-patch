# -*- coding: utf-8 -*-
"""작전파일 빌드 계획(읽기 전용): 본편 원본↔빌드 차이 파일 중 작전에 같은 것/다른 것, 작전 전용 파일."""
import sys, os, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
iK, EK = B.disc('K'); iF, EF = B.disc('F')
bk = Iso(glob.glob('work/disc/*Track 1*.bin')[0]); EB = {f[0]: f for f in bk.walk()}
rd = lambda i, e: i.read(*e[1:3])
same = []; diff = []; none = []
for fn, e in EK.items():
    if fn.endswith('/') or fn.startswith('/CDDA'): continue
    if rd(iK, e) == rd(bk, EB[fn]): continue
    if fn not in EF: none.append((fn, e[2])); continue
    (same if rd(iK, e) == rd(iF, EF[fn]) else diff).append((fn, e[2], EF[fn][2]))
print('본편 고친 파일', len(same) + len(diff) + len(none))
print('작전에 같은 파일(그대로 복사)', len(same), [x[0] for x in same][:80])
print('작전에 있으나 다름', len(diff), diff[:60])
print('작전에 없음', len(none), [x[0] for x in none][:80])
only = [(fn, e[2]) for fn, e in EF.items() if fn not in EK and not fn.endswith('/') and not fn.startswith('/CDDA')]
c = collections.Counter(os.path.dirname(x[0]) for x in only); print('작전 전용', len(only), c.most_common(12))
print([x for x in only if os.path.dirname(x[0]) == ''][:60])
