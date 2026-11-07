# -*- coding: utf-8 -*-
"""줄 폭 전수(읽기 전용): 작전 시나리오 설명(19칸), 본편·작전 UI 줄 중 원문보다 긴 것.  python tools/width_audit.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, ded_build as D, sf_ded as SD, ded_f as DF, ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
N = chr(92) + 'l'
iso, E = B.disc('F'); g = iso.read(*E['/GMS1.BIN'][1:3]); J = SD.table()
print('== 작전 시나리오 설명(칸 39, 줄 19)')
n = 0
for l in open('work/text/f_raw.tsv', encoding='utf-8'):
    nm, o, t = l.rstrip('\n').split('\t')
    if nm != '/GMSFONT.BIN' or SD.nz(t) not in J: continue
    o = int(o, 16); q = o
    while struct.unpack_from('>H', g, q)[0] != 0xFFFF: q += 2
    slot = (q - o) // 2
    if slot < 30: continue
    v = DF.BY_OFF.get(o) or DF.SHORT.get(J[SD.nz(t)], J[SD.nz(t)])
    w = D.wrap(v, 19); L = w.split(N); total = sum(map(len, L)) + len(L) - 1
    bad = max(map(len, L)) > 19 or total > slot or len(L) > 2
    n += bad
    print(('✗' if bad else ' '), hex(o), slot, total, len(L), v.replace(N, ' / '))
print('고칠 줄', n)
k, _, _ = A.load_ko()
print('== UI 줄: 번역이 원문보다 긴 것(칸 기준)')
for tag in 'KF':
    seen = set()
    pos = B.load()
    for (tg, fn), v in pos.items():
        if tg != tag: continue
        for o, n_, i, t in sorted(v):
            if len(t) > n_ and t not in seen:
                seen.add(t); print(tag, fn, hex(o), i, '원문칸', n_, '번역', len(t), t)
