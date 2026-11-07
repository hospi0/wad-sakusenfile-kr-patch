# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import ded_build as D
K = [l.rstrip('\n').split('\t') for l in open('work/text/ko_extra.tsv', encoding='utf-8') if l[0] != '#']
J = {l.split('\t')[0]: l.split('\t')[4] for l in open('work/text/extra.tsv', encoding='utf-8') if l[0] != '#'}
tot = 0; seen = set()
for i, t in K:
    if '01600' <= i <= '01625':
        w = D.wrap(t, 19); n = len(w.replace(D.NL, 'x')) + 1
        if w not in seen: tot += n; seen.add(w)
        if i >= '01614': print(i, len(J[i].replace(D.NL, '')) + 1, n, w.replace(D.NL, ' / '))
print('합(같은 줄 한 벌)', tot, '가능 워드', (0x5DC86 - 0x5D8DC) // 2 + (0x5D8BA - 0x5D8A0) // 2 - 14)
