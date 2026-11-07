# -*- coding: utf-8 -*-
import sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(92) + 'l'
K = {}
for l in open('work/text/ko_extra.tsv', encoding='utf-8'):
    if l[0] != '#':
        p = l.rstrip('\n').split('\t')
        if len(p) > 1: K[p[0]] = p[-1]
R = [l.rstrip('\n').split('\t') for l in open('work/text/extra.tsv', encoding='utf-8') if l[0] != '#' and l.split('\t')[1] == 'Y']
print(len(R), sum(len(r[4]) for r in R), sum(len(K[r[0]]) for r in R))
c = collections.Counter()
for r in R:
    a = r[4].split(NL); b = K[r[0]].split(NL); c[(len(a) == len(b))] += 1
print(c, '번역 최대 줄', max(len(x) for r in R for x in K[r[0]].split(NL)), collections.Counter(len(x) for r in R for x in K[r[0]].split(NL)).most_common(6))
for r in R[:5] + R[60:64] + R[-3:]: print(r[0], r[4][:70].replace(NL, '/'), '\n   ', K[r[0]][:90].replace(NL, '/'))
