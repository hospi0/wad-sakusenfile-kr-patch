# -*- coding: utf-8 -*-
"""전용 글꼴별 필요 글자 수(읽기 전용)."""
import sys, os, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')
def rd(a, b):
    k = {}
    for l in open(b, encoding='utf-8'):
        if l[0] != '#':
            p = l.rstrip('\n').split('\t')
            if len(p) > 1: k[p[0]] = p[-1]
    R = []
    for l in open(a, encoding='utf-8'):
        if l[0] != '#':
            p = l.rstrip('\n').split('\t'); R.append((p[1], p[4], k.get(p[0], '')))
    return R
R = rd('work/text/extra.tsv', 'work/text/ko_extra.tsv') + rd('work/text/extra2.tsv', 'work/text/ko_extra2.tsv')
G = collections.defaultdict(list)
for g, j, k in R: G[g].append(k)
FONT = {'T': 188, 'M+KG': 99, 'R': 88, 'Y': 428, 'FT': 206, 'FG': 371, 'FS': 0, 'FO': 270}
def syl(L): return {c for t in L for c in t if ord(c) > 127 and c not in '　'}
for k, v in (('T', G['T']), ('M+KG', G['M'] + G['KG']), ('R', G['R']), ('Y', G['Y']), ('FT', G['FT'] + G['T']), ('FG', G['FG'] + G['M']), ('FS', G['FS']), ('FO', G['FO'])):
    print(k, '줄', len(v), '빈 번역', sum(not t for t in v), '글자종', len(syl(v)), '칸', FONT[k], '글자', sum(len(t) for t in v))
