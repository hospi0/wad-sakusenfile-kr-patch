# -*- coding: utf-8 -*-
"""반각 글자 수요(읽기 전용)."""
import sys, re, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import ko_audit as A, unit_names as UN
k, _, _ = A.load_ko()
def tsv(f, kf=None):
    K = {}
    if kf:
        for l in open(kf, encoding='utf-8'):
            if l[0] != '#':
                p = l.rstrip('\n').split('\t')
                if len(p) > 1: K[p[0]] = p[-1]
    R = []
    for l in open(f, encoding='utf-8'):
        if l[0] != '#':
            p = l.rstrip('\n').split('\t')
            t = K.get(p[0]) or (k[p[0]][0][5] if p[0] in k else '')
            R.append((p[1], p[4], t))
    return R
G = collections.defaultdict(list)
for f, kf in (('work/text/small.tsv', None), ('work/text/place.tsv', None), ('work/text/small2.tsv', 'work/text/ko_small2.tsv'), ('work/text/small3.tsv', 'work/text/ko_small3.tsv')):
    for g, j, t in tsv(f, kf): G[f[10:-4] + ':' + g].append(t)
allc = collections.Counter(); 
for key, v in G.items():
    c = collections.Counter(ch for t in v for ch in t if '가' <= ch <= '힣'); allc.update(c)
    print(key, len(v), '빈', sum(not t for t in v), '음절', len(c), '최대 길이', max(len(t) for t in v))
print('전체 음절', len(allc), '1회만', sum(1 for x in allc.values() if x == 1))
print('시트 칸', len(UN.S), ''.join(UN.S[i] for i in sorted(UN.S))[:220])
