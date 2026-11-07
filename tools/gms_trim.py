# -*- coding: utf-8 -*-
"""GMS2 글꼴 99칸 맞추기 시험(읽기 전용, 번역 안 바꿈)."""
import sys, collections
sys.stdout.reconfigure(encoding='utf-8')
L = [l.rstrip('\n').split('\t') for f in ('work/text/ko_extra.tsv', 'work/text/ko_extra2.tsv') for l in open(f, encoding='utf-8') if l[0] != '#']
K = {p[0]: p[-1] for p in L if len(p) > 1}
R = [l.split('\t') for f in ('work/text/extra.tsv', 'work/text/extra2.tsv') for l in open(f, encoding='utf-8') if l[0] != '#']
rows = [(r[0], r[4], K.get(r[0], '')) for r in R if r[1] in ('M', 'KG') and K.get(r[0])]
def stat(rows):
    c = collections.Counter(); w = collections.defaultdict(list)
    for i, j, k in rows:
        for x in set(k.replace(' ', '')): c[x] += 1; w[x].append(k)
    return c, w
c, w = stat(rows); print('지금', len(c))
SUB = {'모스크바 4Pz': '모스크바 4기갑', '모스크바 2Pz': '모스크바 2기갑', '오키나와 IJN': '오키나와 해군', '오키나와 32Army': '오키나와 32군', 'MAP 선택 화면': '맵 선택 화면'}
r2 = [(i, j, SUB.get(k, k)) for i, j, k in rows]; c2, w2 = stat(r2); print('영문 정리 뒤', len(c2), sorted(x for x in c2 if ord(x) < 128))
one = sorted((x for x in c2 if c2[x] == 1 and ord(x) > 127), key=lambda x: w2[x][0])
g = collections.defaultdict(list)
for x in one: g[w2[x][0]].append(x)
for k, v in sorted(g.items(), key=lambda t: -len(t[1])): print(k, ''.join(v))
