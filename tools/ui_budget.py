# -*- coding: utf-8 -*-
"""UI 문자열 묶음별 칸 합계(원문 대 번역, 읽기 전용).  python tools/ui_budget.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
m = A.load_master(); k, _, _ = A.load_ko()
rows = [l.rstrip('\n').split('\t') for l in open('work/text/ui_pos.tsv', encoding='utf-8')]
G = collections.defaultdict(list)
for i, tag, fn, o, n in rows:
    o = int(o, 16)
    G[(tag, fn)].append((o, i, int(n)))
for key, v in G.items():
    v.sort(); cur = [v[0]]; blocks = []
    for a, b in zip(v, v[1:]):
        if b[0] - (a[0] + a[2] * 2) > 8: blocks.append(cur); cur = []
        cur.append(b)
    blocks.append(cur)
    for b in blocks:
        if len(b) < 3: continue
        src = sum(x[2] for x in b); ko = sum(max(A.cells(k[x[1]][0][5]), 0) for x in b)
        over = sum(1 for x in b if A.cells(k[x[1]][0][5]) > x[2])
        print(key, hex(b[0][0]), '줄', len(b), '원문 칸', src, '번역 칸', ko, '여유', src - ko, '넘는 줄', over)
