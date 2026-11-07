# -*- coding: utf-8 -*-
"""AWW 작은 글자 영문 표기로 강철 반각 이름 대응(읽기 전용 초안).  --write = work/text/romaji.tsv"""
import sys, re, collections, csv
sys.stdout.reconfigure(encoding='utf-8')
AW = 'C:/claude/project/aww-kr-patch/'
A = {}
for l in open(AW + 'work/smalltext/smalltext.tsv', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 8 and p[1] in ('units', 'places', 'names', 'terrain') and p[7]: A.setdefault(p[4].rstrip(), p[7].rstrip())
print('AWW', len(A), list(A.items())[200:206])
rows = []
for f, g in (('work/text/small.tsv', 'N'), ('work/text/small3.tsv', 'D')):
    for l in open(f, encoding='utf-8'):
        if l[0] != '#':
            p = l.rstrip('\n').split('\t')
            if p[1] == g and not (g == 'D' and int(p[0]) < 1880): rows.append((p[0], p[4], g))
hit = [(i, j, A[j]) for i, j, g in rows if j in A]; miss = [(i, j) for i, j, g in rows if j not in A]
print(len(rows), '맞음', len(hit), '없음', len(miss)); print('한글 섞임', [x for x in hit if re.search('[가-힣]', x[2])][:20], sum(1 for x in hit if re.search('[가-힣]', x[2])))
print(hit[:10]); print([j for i, j in miss][:60])
sys.path.insert(0, 'tools')
import ko_audit as AU
k, _, _ = AU.load_ko()
K3 = dict(l.rstrip('\n').split('\t', 1) for l in open('work/text/ko_small3.tsv', encoding='utf-8') if l[0] != '#')
out = []
for i, j in miss:
    ko = K3.get(i) or (k[i][0][5] if i in k else '')
    out.append('%s %s %s' % (i[1:], j, ko))
print('=====')
print('|'.join(out))
print('=====')
print([ (a, b) for a, b in A.items() if re.search('シキ|ガタ|クラス|Type|Ki|Zero|Hay', a + b)][:30])
